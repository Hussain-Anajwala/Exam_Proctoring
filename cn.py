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
    os.replace(file_path + ".tmp", file_path)

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
            print(f"[CN] Teacher update: rn={rn}, violation={teacher_msg.get('violation_no')}, status={status}, percentage={perc}")
            clear_file(TEACHER_TO_CN_FILE)

            if status == "noted":
                write_message(TEACHER_FILE, {"ack_counter": counter, "rn": rn})
                print(f"[CN] Acked violation {teacher_msg.get('violation_no')} for rn={rn}")
                return "continue", rn
            elif status == "terminate":
                print(f"[CN] Terminating exam for rn={rn}")
                write_message(TEACHER_FILE, {"ack_counter": counter, "rn": rn, "terminated": True})
                write_message(CD_EXAM_OVER_FILE, {"command": "exam_terminated", "rn": rn})
                return "terminated_student", rn
    print(f"[CN] Timeout waiting for Teacher update for counter {counter}")
    return None, None

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
            print("\n================ FINAL MARKSHEET ================")
            for rn, marks in teacher_msg["marks"].items():
                print(f" Roll No {rn}: {marks} marks")
            print("================================================\n")
            clear_file(TEACHER_TO_CN_FILE)
            write_message(TEACHER_FILE, {"command": "marks_report_ack"})
            return teacher_msg
    print("[CN] Timeout waiting for Teacher marks report!")
    return None

def main():
    print("[CN] Starting CN process...")

    nums = []
    counts = {}
    while len(nums) < 5:
        rn = random.randint(1, 3)
        if counts.get(rn, 0) < 2:
            nums.append(rn)
            counts[rn] = counts.get(rn, 0) + 1

    counter = 0
    clear_file(CD_TO_CN_FILE)
    clear_file(TEACHER_TO_CN_FILE)
    clear_file(CD_EXAM_OVER_FILE)

    terminated_students = set()
    violations_count = {}  # NEW: track violation number per student

    for rn in nums:
        if rn in terminated_students:
            print(f"[CN] Skipping rn={rn}, already terminated.")
            continue

        counter += 1
        violations_count[rn] = violations_count.get(rn, 0) + 1

        msg = {
            "rn": rn,
            "name": STUDENT_NAME,
            "warning": WARNING,
            "counter": counter,
            "violation_no": violations_count[rn]
        }
        print(f"[CN] Sending violation {violations_count[rn]} for rn={rn}")

        write_message(CD_FILE, msg)
        write_message(TEACHER_FILE, msg)

        result, affected_rn = wait_for_teacher_update(counter)
        if result == "terminated_student" and affected_rn:
            terminated_students.add(affected_rn)
        elif result is None:
            print(f"[CN] Warning: did not receive teacher update for counter {counter}")

        print(f"[CN] Waiting 5 seconds before next violation...")
        time.sleep(5)

    print("[CN] All questions sent. Waiting for CD exam over request...")

    if not wait_for_cd_exam_over_request():
        print("[CN] Warning: did not receive exam over request from CD")

    write_message(TEACHER_FILE, {"command": "send_marks"})

    marks_report = wait_for_teacher_marks_report()
    if marks_report:
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
