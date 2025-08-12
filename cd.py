import json
import os
import time

COMM_DIR = "./"
CN_FILE = os.path.join(COMM_DIR, "cn_to_cd.json")
CN_EXAM_OVER_FILE = os.path.join(COMM_DIR, "cn_to_cd_exam_over.json")
CD_TO_CN_FILE = os.path.join(COMM_DIR, "cd_to_cn.json")
TEACHER_TO_CD_FILE = os.path.join(COMM_DIR, "teacher_to_cd.json")

current_question = None

def write_message(file_path, data):
    with open(file_path + ".tmp", "w") as f:
        json.dump(data, f)
    os.replace(file_path + ".tmp", file_path)

def read_message(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        try:
            data = json.load(f)
            return data
        except Exception:
            return None

def clear_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def main():
    print("[CD] Starting CD (student) process...")

    exam_over = False

    while True:
        time.sleep(1)
        # Check for question from CN
        msg = read_message(CN_FILE)
        if msg:
            current_question = msg.get("rn")
            print(f"[CD] Received question: {current_question} with warning: {msg.get('warning')}")
            clear_file(CN_FILE)

        # Check for exam over notification
        exam_over_msg = read_message(CN_EXAM_OVER_FILE)
        if exam_over_msg and exam_over_msg.get("command") == "exam_over":
            print("[CD] Received exam over notification.")
            clear_file(CN_EXAM_OVER_FILE)
            exam_over = True

        if exam_over:
            print("[CD] Sending exam over request to CN...")
            write_message(CD_TO_CN_FILE, {"command": "exam_over_request"})

            # Wait for marks report from Teacher
            while True:
                time.sleep(1)
                marks_report = read_message(TEACHER_TO_CD_FILE)
                if marks_report and marks_report.get("command") == "marks_report":
                    print(f"[CD] Received final marks report:\n{marks_report['marks']}")
                    clear_file(TEACHER_TO_CD_FILE)
                    print("[CD] Exam finished. Exiting.")
                    return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CD] Shutting down...")
