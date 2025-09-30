# cn.py
import socket
import random
import time
import threading
import queue
import sys
import os
sys.path.append(r"C:\Users\Saish\Documents\Github\Exam-System")
from utils import send_json, recv_json

TEACHER_ADDR = ("127.0.0.1", 5000)
CD_ADDR = ("127.0.0.1", 5002)

WARNING = "Please focus, exam in progress!"

students_rolls = [58, 59, 65, 75, 68]
students_names = {
    58: "Hussain", 59: "Saish", 65: "Khushal", 75: "Hasnain", 68: "Amritesh"
}

# We'll use threads to read both sockets and push messages into queues
teacher_q = queue.Queue()
cd_q = queue.Queue()

def teacher_reader(sock):
    """
    Background thread reading messages from Teacher and pushing them to teacher_q.
    """
    while True:
        msg = recv_json(sock)
        if not msg:
            print("[CN] Disconnected from Teacher.")
            break
        teacher_q.put(msg)

def cd_reader(sock):
    """
    Background thread reading messages from CD and pushing them to cd_q.
    """
    while True:
        msg = recv_json(sock)
        if not msg:
            print("[CN] Disconnected from CD.")
            break
        cd_q.put(msg)

def wait_for_teacher_update(counter, timeout=15):
    """
    Wait until teacher_q yields a message with matching counter within timeout seconds.
    Returns tuple (result, roll) where result is "continue" / "terminated_student" / None.
    """
    waited = 0
    while waited < timeout:
        try:
            msg = teacher_q.get(timeout=1)
        except queue.Empty:
            waited += 1
            continue
        if msg.get("counter") == counter:
            status = msg.get("status")
            roll = msg.get("roll")
            if status == "noted":
                # send ack back to teacher (ack_counter)
                # The ack should be sent over the teacher socket, but we don't have direct access here.
                # Store ack request by returning result and letting main thread send it.
                return "continue", roll
            elif status == "terminate":
                return "terminated_student", roll
        # ignore other teacher messages here (like marks_report)
    return None, None

def wait_for_cd_exam_over_request(timeout=15, cd_sock=None):
    """
    Wait for CD to send 'exam_over_request' to CN (via cd_q).
    """
    waited = 0
    while waited < timeout:
        try:
            msg = cd_q.get(timeout=1)
        except queue.Empty:
            waited += 1
            continue
        if msg.get("command") == "exam_over_request":
            return True
    return False

def wait_for_teacher_marks_report_print(teacher_sock):
    """
    This prints the final marks when Teacher sends them to CN (via teacher_q).
    """
    print("\n📄 Final Marksheet (via CN):")
    print(" Roll | Name      | Marks ")
    print("---------------------------")
    while True:
        msg = teacher_q.get()
        if msg and msg.get("command") == "marks_report":
            marks = msg.get("marks", {})
            for roll_str, mark in marks.items():
                roll = int(roll_str)
                name = students_names.get(roll, "Unknown")
                print(f" {roll:<4} | {name:<9} | {mark}")
            # Acknowledge to teacher that CN got the marks
            try:
                send_json(teacher_sock, {"command": "marks_report_ack"})
            except Exception:
                pass
            break

def main():
    # Connect to Teacher
    t_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            t_sock.connect(TEACHER_ADDR)
            break
        except Exception as e:
            print(f"[CN] Waiting for Teacher at {TEACHER_ADDR}... ({e})")
            time.sleep(1)
    send_json(t_sock, {"role": "CN"})
    threading.Thread(target=teacher_reader, args=(t_sock,), daemon=True).start()

    # Connect to CD (server)
    cd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            cd_sock.connect(CD_ADDR)
            break
        except Exception as e:
            print(f"[CN] Waiting for CD server at {CD_ADDR}... ({e})")
            time.sleep(1)
    send_json(cd_sock, {"role": "CN"})
    threading.Thread(target=cd_reader, args=(cd_sock,), daemon=True).start()

    nums = []
    counts = {}
    terminated_students = set()
    violations_count = {}

    counter = 0

    # Generate 5 random question violations (same logic as original)
    while len(nums) < 5:
        roll = random.choice(students_rolls)
        if counts.get(roll, 0) < 2:
            nums.append(roll)
            counts[roll] = counts.get(roll, 0) + 1

    for roll in nums:
        if roll in terminated_students:
            continue

        counter += 1
        violations_count[roll] = violations_count.get(roll, 0) + 1
        question_no = random.randint(1, 50)

        msg = {
            "roll": roll,
            "name": students_names[roll],
            "warning": WARNING,
            "counter": counter,
            "question_no": question_no,
            "violation_no": violations_count[roll]
        }

        # Send to CD and Teacher
        try:
            send_json(cd_sock, msg)
        except Exception:
            print("[CN] Failed sending to CD.")
        try:
            send_json(t_sock, msg)
        except Exception:
            print("[CN] Failed sending to Teacher.")

        # Wait for teacher update for this counter
        result, affected_roll = wait_for_teacher_update(counter, timeout=15)
        if result == "continue":
            # send ack to teacher for this counter
            try:
                send_json(t_sock, {"ack_counter": counter, "roll": roll})
            except Exception:
                pass
        elif result == "terminated_student" and affected_roll:
            # Send ack + terminated flag to teacher, and forward exam_terminated to CD
            try:
                send_json(t_sock, {"ack_counter": counter, "roll": affected_roll, "terminated": True})
            except Exception:
                pass
            try:
                send_json(cd_sock, {"command": "exam_terminated", "roll": affected_roll})
            except Exception:
                pass
            terminated_students.add(affected_roll)
        else:
            # Timeout or nothing -> ignore and continue
            pass

        time.sleep(2)

    # Now wait for CD's exam_over_request (CD will request CN to ask teacher for marks)
    got = wait_for_cd_exam_over_request(timeout=15)
    if got:
        # CN requests Teacher to send marks
        try:
            send_json(t_sock, {"command": "send_marks"})
        except Exception:
            pass

    # Print marks when teacher sends them to CN
    wait_for_teacher_marks_report_print(t_sock)

    # after done, allow some grace time for CD->CN ack to arrive (not strictly needed)
    time.sleep(1)
    try:
        t_sock.close()
    except:
        pass
    try:
        cd_sock.close()
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CN] Shutting down...")
