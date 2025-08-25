import json
import os
import random
import time

COMM_DIR = "./"
CD_FILE = os.path.join(COMM_DIR, "cn_to_cd.json")
TEACHER_FILE = os.path.join(COMM_DIR, "cn_to_teacher.json")
CD_EXAM_OVER_FILE = os.path.join(COMM_DIR, "cn_to_cd_exam_over.json")
CD_TO_CN_FILE = os.path.join(COMM_DIR, "cd_to_cn.json")
TEACHER_TO_CN_FILE = os.path.join(COMM_DIR, "teacher_to_cn.json")

STUDENT_NAME = "Student_1"
WARNING = "Please focus, exam in progress!"

def write_message(file_path, data):
    with open(file_path + ".tmp", "w") as f:
        json.dump(data, f)
    os.replace(file_path + ".tmp", file_path)  # atomic replace

def read_message(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return None

def clear_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def wait_for_teacher_update(counter, timeout=15):
    """
    Wait for Teacher response. If 'noted' → ack back.
    If 'terminate' → end exam for that rn and stop further processing.
    """
    print(f"[CN] Waiting for teacher update for counter {counter} (timeout {timeout}s)...")
    waited = 0
    while waited < timeout:
        time.sleep(1)
        waited += 1
        teacher_msg = read_message(TEACHER_TO_CN_FILE)
        if teacher_msg and teacher_msg.get("counter") == counter:
            rn = teacher_msg.get("rn")
            status = teacher_msg.get("status")
            perc = teacher_msg.get("percentage")
            print(f"[CN] Teacher update: rn={rn}, counter={counter}, status={status}, percentage={perc}")
            clear_file(TEACHER_TO_CN_FILE)

            if status == "noted":
                # Send ack back
                write_message(TEACHER_FILE, {"ack_counter": counter, "rn": rn})
                print(f"[CN] Acked first violation for rn={rn}")
                return "continue"
            elif status == "terminate":
                # Terminate exam for this rn
                print(f"[CN] Terminating exam for rn={rn}")
                write_message(TEACHER_FILE, {"ack_counter": counter, "rn": rn, "terminated": True})
                write_message(CD_EXAM_OVER_FILE, {"command": "exam_terminated", "rn": rn})
                return "terminate"
    print(f"[CN] Timeout waiting for Teacher update for counter {counter}")
    return None

def wait_for_cd_exam_over_request(timeout=15):
    print(f"[CN] Waiting for CD exam over request (timeout {timeout}s)...")
    waited = 0
    while waited < timeout:
        time.sleep(1)
        waited += 1
        cd_msg = read_message(CD_TO_CN_FILE)
        if cd_msg and cd_msg.get("command") == "exam_over_request":
            print("[CN] Received exam over request from CD, forwarding to Teacher.")
            clear_file(CD_TO_CN_FILE)
            return True
    print("[CN] Timeout waiting for CD exam over request!")
    return False

def wait_for_teacher_marks_report(timeout=15):
    print(f"[CN] Waiting for marks report from Teacher (timeout {timeout}s)...")
    waited = 0
    while waited < timeout:
        time.sleep(1)
        waited += 1
        teacher_msg = read_message(TEACHER_TO_CN_FILE)
        if teacher_msg and teacher_msg.get("command") == "marks_report":
            print(f"[CN] Received marks report: {teacher_msg['marks']}")
            clear_file(TEACHER_TO_CN_FILE)
            write_message(TEACHER_FILE, {"command": "marks_report_ack"})
            return teacher_msg
    print("[CN] Timeout waiting for Teacher marks report!")
    return None

def main():
    print("[CN] Starting CN process...")

    # Generate 5 random numbers between 1-69, no number repeats >2 times
    nums = []
    counts = {}
    while len(nums) < 5:
        rn = random.randint(1, 3)
        if counts.get(rn, 0) < 2:
            nums.append(rn)
            counts[rn] = counts.get(rn, 0) + 1

    counter = 0

    # Clear leftover files
    clear_file(CD_TO_CN_FILE)
    clear_file(TEACHER_TO_CN_FILE)
    clear_file(CD_EXAM_OVER_FILE)

    exam_terminated = False

    for rn in nums:
        if exam_terminated:
            print("[CN] Exam already terminated, skipping further questions.")
            break

        counter += 1
        msg = {"rn": rn, "name": STUDENT_NAME, "warning": WARNING, "counter": counter}
        print(f"[CN] Sending question #{counter}: {rn}")

        # Send to CD and Teacher
        write_message(CD_FILE, msg)
        write_message(TEACHER_FILE, msg)

        # Wait for Teacher update
        result = wait_for_teacher_update(counter)
        if result == "terminate":
            exam_terminated = True
            break
        elif result is None:
            print(f"[CN] Warning: did not receive teacher update for counter {counter}")

        # Wait before next number (if exam not terminated)
        if not exam_terminated:
            print(f"[CN] Waiting 15 seconds before next question...")
            time.sleep(15)

    if not exam_terminated:
        print("[CN] All questions sent. Waiting for CD exam over request...")

        # Wait for CD exam over request (e.g., exam naturally ends)
        if not wait_for_cd_exam_over_request():
            print("[CN] Warning: did not receive exam over request from CD")

    # Forward exam over request / termination to Teacher
    write_message(TEACHER_FILE, {"command": "send_marks"})

    # Wait for Teacher marks report
    marks_report = wait_for_teacher_marks_report()
    if marks_report:
        # Send to CD
        write_message(os.path.join(COMM_DIR, "teacher_to_cd.json"), marks_report)
        print("[CN] Sent marks report to CD.")
    else:
        print("[CN] Warning: marks report missing, exam incomplete.")

    print("[CN] Exam workflow complete.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CN] Shutting down...")
