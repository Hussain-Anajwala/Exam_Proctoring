import json
import os
import time

COMM_DIR = "./"
CN_FILE = os.path.join(COMM_DIR, "cn_to_cd.json")
CN_EXAM_OVER_FILE = os.path.join(COMM_DIR, "cn_to_cd_exam_over.json")
CD_TO_CN_FILE = os.path.join(COMM_DIR, "cd_to_cn.json")
TEACHER_TO_CD_FILE = os.path.join(COMM_DIR, "teacher_to_cd.json")

students_names = {
    58: "Hussain", 
    59: "Saish", 
    65: "Khushal", 
    75: "Hasnain", 
    68: "Amritesh"
}

violations = {}          # track violations per roll
terminated_students = set()

def write_message(file_path, data):
    with open(file_path + ".tmp", "w") as f:
        f.seek(0)
        json.dump(data, f)
        f.truncate()
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

def main():
    exam_over = False

    while True:
        time.sleep(1)
        msg = read_message(CN_FILE)
        if msg:
            roll = msg.get("roll")
            warning = msg.get("warning")
            name = students_names.get(roll, "Unknown")

            # skip if already terminated
            if roll in terminated_students:
                clear_file(CN_FILE)
                continue

            # count violations
            violations[roll] = violations.get(roll, 0) + 1
            count = violations[roll]

            if count == 1:
                print(f"[CD] WARNING → {name} (Roll {roll}): Violation 1 - {warning}")
            elif count == 2:
                print(f"[CD] TERMINATED → {name} (Roll {roll}) due to 2nd violation (marks = 0)")
                terminated_students.add(roll)

            write_message(CD_TO_CN_FILE, {"ack_rn": roll, "ack_type": "question"})
            clear_file(CN_FILE)

        # Handle exam over / marks report
        exam_over_msg = read_message(CN_EXAM_OVER_FILE)
        if exam_over_msg:
            command = exam_over_msg.get("command")
            roll = exam_over_msg.get("roll")

            if command == "exam_over":
                exam_over = True
            clear_file(CN_EXAM_OVER_FILE)

        if exam_over:
            write_message(CD_TO_CN_FILE, {"command": "exam_over_request"})
            while True:
                time.sleep(1)
                marks_report = read_message(TEACHER_TO_CD_FILE)
                if marks_report and marks_report.get("command") == "marks_report":
                    print("\n📄 Final Marksheet (via CD):")
                    print(" Roll | Name      | Marks ")
                    print("---------------------------")
                    for roll, marks in marks_report["marks"].items():
                        roll = int(roll)  # ensure string keys become int
                        name = students_names.get(roll, "Unknown")
                        print(f" {roll:<4} | {name:<9} | {marks}")
                    clear_file(TEACHER_TO_CD_FILE)
                    write_message(CD_TO_CN_FILE, {"command": "marks_report_ack"})
                    return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CD] Shutting down...")
