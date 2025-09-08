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

WARNING = "Please focus, exam in progress!"

# predefined student rolls/names (must match teacher.py)
students_rolls = [58, 59, 65, 75, 68]
students_names = {
    58: "Hussain", 59: "Saish", 65: "Khushal", 75: "Hasnain", 68: "Amritesh"
}

def write_message(file_path, data):
    with open(file_path + ".tmp", "w") as f:
        # json.dump(data, f)
        f.seek(0)         # go to start
        json.dump(data, f) # overwrite fresh JSON
        f.truncate()      # remove leftovers
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
    waited = 0
    while waited < timeout:
        time.sleep(1)
        waited += 1
        teacher_msg = read_message(TEACHER_TO_CN_FILE)
        if teacher_msg and teacher_msg.get("counter") == counter:
            roll = teacher_msg.get("roll")
            status = teacher_msg.get("status")
            perc = teacher_msg.get("percentage")
            clear_file(TEACHER_TO_CN_FILE)

            if status == "noted":
                write_message(TEACHER_FILE, {"ack_counter": counter, "roll": roll})
                return "continue", roll
            elif status == "terminate":
                write_message(TEACHER_FILE, {"ack_counter": counter, "roll": roll, "terminated": True})
                write_message(CD_EXAM_OVER_FILE, {"command": "exam_terminated", "roll": roll})
                return "terminated_student", roll
    return None, None

def wait_for_cd_exam_over_request(timeout=15):
    waited = 0
    while waited < timeout:
        time.sleep(1)
        waited += 1
        cd_msg = read_message(CD_TO_CN_FILE)
        if cd_msg and cd_msg.get("command") == "exam_over_request":
            clear_file(CD_TO_CN_FILE)
            return True
    return False

def wait_for_teacher_marks_report():
    print("\n📄 Final Marksheet (via CN):")
    print(" Roll | Name      | Marks ")
    print("---------------------------")
    while True:
        msg = read_message(TEACHER_TO_CN_FILE)
        if msg and msg.get("command") == "marks_report":
            marks = msg.get("marks", {})
            for roll_str, mark in marks.items():
                roll = int(roll_str)  # convert key from str → int
                name = students_names.get(roll, "Unknown")
                print(f" {roll:<4} | {name:<9} | {mark}")
            break
        time.sleep(1)

def main():
    nums = []
    counts = {}
    terminated_students = set()
    violations_count = {}

    counter = 0
    clear_file(CD_TO_CN_FILE)
    clear_file(TEACHER_TO_CN_FILE)
    clear_file(CD_EXAM_OVER_FILE)

    # Generate 5 random question violations
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

        write_message(CD_FILE, msg)
        write_message(TEACHER_FILE, msg)

        result, affected_roll = wait_for_teacher_update(counter)
        if result == "terminated_student" and affected_roll:
            terminated_students.add(affected_roll)

        time.sleep(2)

    if not wait_for_cd_exam_over_request():
        pass

    write_message(TEACHER_FILE, {"command": "send_marks"})
    wait_for_teacher_marks_report()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CN] Shutting down...")
