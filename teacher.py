import json
import os
import time

COMM_DIR = "./"
CN_FILE = os.path.join(COMM_DIR, "cn_to_teacher.json")
TEACHER_TO_CN_FILE = os.path.join(COMM_DIR, "teacher_to_cn.json")
TEACHER_TO_CD_FILE = os.path.join(COMM_DIR, "teacher_to_cd.json")

# predefined student marksheet
students = { 
    1: {"roll": 58, "name": "Hussain", "violation": 0}, 
    2: {"roll": 59, "name": "Saish", "violation": 0}, 
    3: {"roll": 65, "name": "Khushal", "violation": 0}, 
    4: {"roll": 75, "name": "Hasnain", "violation": 0}, 
    5: {"roll": 68, "name": "Amritesh", "violation": 0}, 
}

# Initialize marksheet: all students start with 100 marks
marksheet = {s["roll"]: 100 for s in students.values()}

# Track state for each student
student_states = {
    s["roll"]: {"violations": 0, "percentage": 100, "name": s["name"]}
    for s in students.values()
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

def handle_violation(msg):
    roll = msg.get("roll")
    question_no = msg.get("question_no", -1)
    name = msg.get("name") or f"Roll_{roll}"

    state = student_states[roll]
    state["violations"] += 1
    vcount = state["violations"]

    if vcount == 1:
        state["percentage"] = 50
        status = "noted"
    elif vcount == 2:
        state["percentage"] = 0
        status = "terminate"
    else:
        print(f"[Teacher] Roll {roll} already terminated → ignoring.")
        return

    marksheet[roll] = state["percentage"]

    print(f"[Teacher] Violation {vcount} for roll {roll} on Q{question_no}, percentage={state['percentage']}")
    write_message(TEACHER_TO_CN_FILE, {
        "roll": roll,
        "violation": vcount,
        "question_no": question_no,
        "percentage": state["percentage"],
        "status": status
    })

def handle_command(msg):
    cmd = msg.get("command")
    if cmd == "send_marks":
        print("[Teacher] Preparing final marksheet...")
        report = {"command": "marks_report", "marks": marksheet}
        write_message(TEACHER_TO_CN_FILE, report)
        write_message(TEACHER_TO_CD_FILE, report)
        print("[Teacher] Marks report sent to CN and CD.")
    elif cmd == "marks_report_ack":
        print("[Teacher] Marks report acknowledged by CN/CD → done.")

def process_message(msg):
    print(f"[Teacher] Incoming msg: {msg}")

    if "ack_counter" in msg:
        print(f"[Teacher] Ack received from CN for counter={msg['ack_counter']} (roll={msg.get('roll')}) → ignoring.")
        return

    if "command" in msg:
        handle_command(msg)
        return

    if "roll" in msg and "question_no" in msg:
        handle_violation(msg)
        return

    print("[Teacher] ⚠️ Unknown message format, skipping...")

def main():
    print("[Teacher] Starting Teacher process...")
    while True:
        time.sleep(1)
        msg = read_message(CN_FILE)
        if msg:
            process_message(msg)
            clear_file(CN_FILE)

def safe_shutdown():
    print("[Teacher] Shutting down...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_shutdown()
