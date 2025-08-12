# import json 
# import os
# import time

# COMM_DIR = "./"
# CN_FILE = os.path.join(COMM_DIR, "cn_to_teacher.json")
# TEACHER_TO_CN_FILE = os.path.join(COMM_DIR, "teacher_to_cn.json")
# TEACHER_TO_CD_FILE = os.path.join(COMM_DIR, "teacher_to_cd.json")

# marksheet = []
# percentage = 100
# current_counter = 0

# def write_message(file_path, data):
#     with open(file_path + ".tmp", "w") as f:
#         json.dump(data, f)
#     os.replace(file_path + ".tmp", file_path)

# def read_message(file_path):
#     if not os.path.exists(file_path):
#         return None
#     with open(file_path, "r") as f:
#         try:
#             data = json.load(f)
#             return data
#         except Exception:
#             return None

# def clear_file(file_path):
#     if os.path.exists(file_path):
#         os.remove(file_path)

# def wait_for_cn_ack(counter, timeout=60):
#     """Wait for CN to acknowledge marks update for a given counter."""
#     waited = 0
#     while waited < timeout:
#         time.sleep(1)
#         waited += 1
#         msg = read_message(CN_FILE)
#         if msg and msg.get("ack_counter") == counter:
#             clear_file(CN_FILE)
#             return True
#     print(f"[Teacher] Timeout waiting for CN ack for counter {counter}")
#     return False

# def process_question(msg):
#     global current_counter, percentage
#     rn = msg["rn"]
#     name = msg["name"]
#     counter = msg["counter"]
#     current_counter = counter

#     # Check if this question already recorded
#     for row in marksheet:
#         if row.get("counter") == counter:
#             return  # already processed

#     # Add entry with current percentage and counter
#     marksheet.append({"Sr": len(marksheet)+1, "rn": rn, "name": name, "percentage": percentage, "counter": counter})
#     print(f"[Teacher] Recorded question {counter}: rn={rn}, name={name}, percentage={percentage}")

#     # After receiving question, reduce marks from 100 to 50 once
#     if percentage == 100:
#         percentage = 50
#         print("[Teacher] Reduced percentage from 100 to 50.")
#         # Notify CN marks updated
#         write_message(TEACHER_TO_CN_FILE, {"counter": counter, "percentage": percentage})
#         # Wait for CN ack before proceeding
#         if not wait_for_cn_ack(counter):
#             print(f"[Teacher] Warning: No ack received from CN for question {counter}")

# def process_commands(msg):
#     global percentage
#     if msg.get("command") == "final_marks":
#         # Change percentage to 0
#         percentage = msg.get("percentage", 0)
#         print("[Teacher] Final marks update to 0%.")
#         # Update all entries
#         for row in marksheet:
#             row["percentage"] = percentage
#         # Acknowledge to CN
#         write_message(TEACHER_TO_CN_FILE, {"command": "final_marks_ack"})
#         # Wait for CN ack on final marks ack
#         waited = 0
#         while waited < 60:
#             time.sleep(1)
#             waited += 1
#             ack = read_message(CN_FILE)
#             if ack and ack.get("command") == "final_marks_ack_received":
#                 clear_file(CN_FILE)
#                 break

#     elif msg.get("command") == "send_marks":
#         # Prepare marks report and send to CN (and indirectly to CD)
#         print("[Teacher] Sending marks report...")
#         marks_report = {"command": "marks_report", "marks": marksheet}
#         write_message(TEACHER_TO_CN_FILE, marks_report)
#         # Wait for CN ack for marks_report
#         waited = 0
#         while waited < 60:
#             time.sleep(1)
#             waited += 1
#             ack = read_message(CN_FILE)
#             if ack and ack.get("command") == "marks_report_ack":
#                 clear_file(CN_FILE)
#                 break

# def main():
#     print("[Teacher] Starting Teacher process...")

#     while True:
#         time.sleep(1)
#         msg = read_message(CN_FILE)
#         if msg:
#             if "command" in msg:
#                 process_commands(msg)
#             else:
#                 process_question(msg)
#             clear_file(CN_FILE)

# def safe_shutdown():
#     print("[Teacher] Shutting down...")

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         safe_shutdown()

import json 
import os
import time

COMM_DIR = "./"
CN_FILE = os.path.join(COMM_DIR, "cn_to_teacher.json")
TEACHER_TO_CN_FILE = os.path.join(COMM_DIR, "teacher_to_cn.json")
TEACHER_TO_CD_FILE = os.path.join(COMM_DIR, "teacher_to_cd.json")

marksheet = []
percentage = 100
current_counter = 0

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

def wait_for_cn_ack(counter, timeout=15):
    waited = 0
    while waited < timeout:
        time.sleep(1)
        waited += 1
        msg = read_message(CN_FILE)
        if msg and msg.get("ack_counter") == counter:
            clear_file(CN_FILE)
            return True
    print(f"[Teacher] Timeout waiting for CN ack for counter {counter}")
    return False

def process_question(msg):
    global current_counter, percentage
    rn = msg["rn"]
    name = msg["name"]
    counter = msg["counter"]
    current_counter = counter

    for row in marksheet:
        if row.get("counter") == counter:
            return

    marksheet.append({"Sr": len(marksheet)+1, "rn": rn, "name": name, "percentage": percentage, "counter": counter})
    print(f"[Teacher] Recorded question {counter}: rn={rn}, name={name}, percentage={percentage}")

    if percentage == 100:
        percentage = 50
        print("[Teacher] Reduced percentage from 100 to 50.")
        write_message(TEACHER_TO_CN_FILE, {"counter": counter, "percentage": percentage})
        wait_for_cn_ack(counter)

def process_commands(msg):
    global percentage
    if msg.get("command") == "final_marks":
        percentage = msg.get("percentage", 0)
        print("[Teacher] Final marks update to 0%.")
        for row in marksheet:
            row["percentage"] = percentage
        write_message(TEACHER_TO_CN_FILE, {"command": "final_marks_ack"})

        waited = 0
        while waited < 15:
            time.sleep(1)
            waited += 1
            ack = read_message(CN_FILE)
            if ack and ack.get("command") == "final_marks_ack_received":
                clear_file(CN_FILE)
                break

    elif msg.get("command") == "send_marks":
        print("[Teacher] Sending marks report...")
        marks_report = {"command": "marks_report", "marks": marksheet}
        write_message(TEACHER_TO_CN_FILE, marks_report)

        waited = 0
        while waited < 15:
            time.sleep(1)
            waited += 1
            ack = read_message(CN_FILE)
            if ack and ack.get("command") == "marks_report_ack":
                clear_file(CN_FILE)
                break

def main():
    print("[Teacher] Starting Teacher process...")
    while True:
        time.sleep(1)
        msg = read_message(CN_FILE)
        if msg:
            if "command" in msg:
                process_commands(msg)
            else:
                process_question(msg)
            clear_file(CN_FILE)

def safe_shutdown():
    print("[Teacher] Shutting down...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_shutdown()
