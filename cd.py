import json
import os
import time

COMM_DIR = "./"
CN_FILE = os.path.join(COMM_DIR, "cn_to_cd.json")
CN_EXAM_OVER_FILE = os.path.join(COMM_DIR, "cn_to_cd_exam_over.json")
CD_TO_CN_FILE = os.path.join(COMM_DIR, "cd_to_cn.json")
TEACHER_TO_CD_FILE = os.path.join(COMM_DIR, "teacher_to_cd.json")

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

def main():
    print("[CD] Starting CD (student) process...")

    exam_over = False
    terminated_students = set()

    while True:
        time.sleep(1)

        # 📩 Check for question/warning from CN
        msg = read_message(CN_FILE)
        if msg:
            rn = msg.get("rn")
            warning = msg.get("warning")

            if rn in terminated_students:
                print(f"[CD] Ignoring question for rn={rn}, already terminated.")
            else:
                print(f"[CD] Received question for rn={rn}, warning: {warning}")

            # Acknowledge receipt to CN
            write_message(CD_TO_CN_FILE, {"ack_rn": rn, "ack_type": "question"})
            clear_file(CN_FILE)

        # 📩 Check for exam over / terminated notification from CN
        exam_over_msg = read_message(CN_EXAM_OVER_FILE)
        if exam_over_msg:
            command = exam_over_msg.get("command")

            if command == "exam_over":
                print("[CD] Received exam over notification.")
                exam_over = True
                # Ack back to CN
                write_message(CD_TO_CN_FILE, {"command": "exam_over_ack"})

            elif command == "exam_terminated":
                rn = exam_over_msg.get("rn")
                print(f"[CD] Received exam TERMINATED notification for rn={rn}.")
                terminated_students.add(rn)
                # Ack back to CN
                write_message(CD_TO_CN_FILE, {"ack_rn": rn, "ack_type": "terminated"})

            clear_file(CN_EXAM_OVER_FILE)

        # 📩 Once exam is over, request marksheet
        if exam_over:
            print("[CD] Sending exam over request to CN...")
            write_message(CD_TO_CN_FILE, {"command": "exam_over_request"})

            # Wait for marks report from Teacher
            while True:
                time.sleep(1)
                marks_report = read_message(TEACHER_TO_CD_FILE)

                if marks_report and marks_report.get("command") == "marks_report":
                    print("[CD] Received final marks report:")
                    for entry in marks_report["marks"]:
                        print(f"  Sr={entry['Sr']} | rn={entry['rn']} | "
                              f"name={entry['name']} | percentage={entry['percentage']}")

                    clear_file(TEACHER_TO_CD_FILE)

                    # Acknowledge marks receipt to Teacher
                    write_message(CD_TO_CN_FILE, {"command": "marks_report_ack"})
                    print("[CD] Exam finished. Exiting.")
                    return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CD] Shutting down...")
