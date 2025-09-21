# cd.py
import socket
import threading
import time
import sys
import os
sys.path.append(r"C:\Users\Saish\Documents\Github\Exam-System")
from utils import send_json, recv_json

TEACHER_ADDR = ("127.0.0.1", 5000)
CD_HOST = "127.0.0.1"
CD_PORT = 5002

students_names = {
    58: "Hussain", 59: "Saish", 65: "Khushal", 75: "Hasnain", 68: "Amritesh"
}

violations = {}          # track violations per roll
terminated_students = set()

# We'll store the connected CN socket (the one that connected to this CD server)
cn_sock = None
cn_sock_lock = threading.Lock()

# Socket connected to teacher (client)
teacher_sock = None

def handle_cn_connection(sock, addr):
    global cn_sock
    with cn_sock_lock:
        cn_sock = sock
    print(f"[CD] CN connected from {addr}")
    try:
        while True:
            msg = recv_json(sock)
            if not msg:
                break

            # Expect violation messages or exam_terminated commands
            if "roll" in msg and "warning" in msg:
                roll = msg.get("roll")
                name = students_names.get(roll, "Unknown")
                # skip if already terminated
                if roll in terminated_students:
                    # send ack back to CN and continue
                    send_json(sock, {"ack_rn": roll, "ack_type": "question"})
                    continue

                violations[roll] = violations.get(roll, 0) + 1
                count = violations[roll]
                if count == 1:
                    print(f"[CD] WARNING → {name} (Roll {roll}): Violation 1 - {msg.get('warning')}")
                elif count == 2:
                    print(f"[CD] TERMINATED → {name} (Roll {roll}) due to 2nd violation (marks = 0)")
                    terminated_students.add(roll)

                # send ack back to CN about the question (similar to file version)
                send_json(sock, {"ack_rn": roll, "ack_type": "question"})

            elif msg.get("command") == "exam_terminated":
                # CN forwarded termination; set exam_over flag by telling CN to request marks
                print(f"[CD] Received exam_terminated for roll {msg.get('roll')}, will request exam_over sequence.")
                # Ask CN to request marks from teacher (original: write CD_TO_CN_FILE with exam_over_request)
                send_json(sock, {"command": "exam_over_request"})
                # After requesting CN to ask teacher, CD waits to receive marks from teacher connection
                # (the teacher will send marks directly to CD, because CD is connected to teacher)
                # We'll wait in below loop once exam_over_request is sent.
            else:
                print(f"[CD] Unknown message from CN: {msg}")

    finally:
        with cn_sock_lock:
            if cn_sock == sock:
                cn_sock = None
        try:
            sock.close()
        except:
            pass
        print("[CD] CN disconnected.")

def cd_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((CD_HOST, CD_PORT))
    server.listen(2)
    print(f"[CD] Server running on {CD_HOST}:{CD_PORT} (waiting for CN)...")
    try:
        while True:
            sock, addr = server.accept()
            # Expect CN to send an initial role declaration
            role_msg = recv_json(sock)
            role = role_msg.get("role") if isinstance(role_msg, dict) else "CN"
            threading.Thread(target=handle_cn_connection, args=(sock, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[CD] Server shutting down...")
    finally:
        server.close()

def teacher_listener_loop(sock):
    """
    Listen for messages from teacher (teacher will send marks_report).
    """
    while True:
        msg = recv_json(sock)
        if not msg:
            print("[CD] Lost connection to Teacher.")
            break
        # If teacher sends final marks
        if msg.get("command") == "marks_report":
            print("\n📄 Final Marksheet (via CD):")
            print(" Roll | Name      | Marks ")
            print("---------------------------")
            marks = msg.get("marks", {})
            for roll_str, marks_val in marks.items():
                roll = int(roll_str)
                name = students_names.get(roll, "Unknown")
                print(f" {roll:<4} | {name:<9} | {marks_val}")
            # Acknowledge back to CN that CD has printed marks
            with cn_sock_lock:
                if cn_sock:
                    try:
                        send_json(cn_sock, {"command": "marks_report_ack"})
                    except Exception:
                        pass
            # Also notify teacher (optional) that CD received marks
            try:
                send_json(sock, {"command": "marks_report_ack"})
            except Exception:
                pass
            # After printing the marks, CD exits
            return

def connect_to_teacher_and_listen():
    global teacher_sock
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(TEACHER_ADDR)
            # Identify to Teacher
            send_json(s, {"role": "CD"})
            teacher_sock = s
            print(f"[CD] Connected to Teacher at {TEACHER_ADDR}")
            teacher_listener_loop(s)
            # if listener returns, connection was lost — try reconnect after delay
        except Exception as e:
            print(f"[CD] Could not connect to Teacher: {e}. Retrying in 1s...")
            time.sleep(1)
        finally:
            try:
                if teacher_sock:
                    teacher_sock.close()
            except:
                pass
            teacher_sock = None
        time.sleep(1)

if __name__ == "__main__":
    try:
        # Start thread to connect to teacher and listen
        threading.Thread(target=connect_to_teacher_and_listen, daemon=True).start()
        # Start server for CN
        cd_server()
    except KeyboardInterrupt:
        print("\n[CD] Shutting down...")
