import json
import os
import time

COMM_DIR = "./"
CN_FILE = os.path.join(COMM_DIR, "cn_to_teacher.json")
TEACHER_TO_CN_FILE = os.path.join(COMM_DIR, "teacher_to_cn.json")
TEACHER_TO_CD_FILE = os.path.join(COMM_DIR, "teacher_to_cd.json")

# marksheet will now be a dict so CN can use .items()
marksheet = {}
student_states = {}   # track per-student state: {rn: {"violations": int, "percentage": int, "name": str}}

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

def handle_violation(msg):
    """Process a violation message from CN (per student tracking)."""
    rn = msg.get("rn")
    name = msg.get("name", f"RN_{rn}")
    counter = msg.get("counter", -1)

    # init student state if first time
    if rn not in student_states:
        student_states[rn] = {"violations": 0, "percentage": 100, "name": name}

    state = student_states[rn]

    # increment violations
    state["violations"] += 1
    vcount = state["violations"]

    if vcount == 1:
        state["percentage"] = 50
        status = "noted"
    elif vcount == 2:
        state["percentage"] = 0
        status = "terminate"
    else:
        print(f"[Teacher] Further violation for rn={rn}, already terminated → ignoring.")
        return

    # update marksheet dict instead of list
    marksheet[rn] = state["percentage"]

    print(f"[Teacher] Violation {vcount} for rn={rn}, percentage={state['percentage']}")

    # notify CN about updated status
    write_message(TEACHER_TO_CN_FILE, {
        "rn": rn,
        "violation": vcount,     # include violation number
        "counter": counter,      # still echo counter back so CN can match
        "percentage": state["percentage"],
        "status": status
    })

def handle_command(msg):
    """Handle control commands from CN/CD."""
    cmd = msg.get("command")

    if cmd == "send_marks":
        print("[Teacher] Preparing final marksheet...")
        report = {"command": "marks_report", "marks": marksheet}
        # send to CN
        write_message(TEACHER_TO_CN_FILE, report)
        # also send to CD
        write_message(TEACHER_TO_CD_FILE, report)
        print("[Teacher] Marks report sent to CN and CD.")

    elif cmd == "marks_report_ack":
        print("[Teacher] Marks report acknowledged by CN/CD → done.")

def process_message(msg):
    print(f"[Teacher] Incoming msg: {msg}")

    # Ignore CN ack (just log it)
    if "ack_counter" in msg:
        print(f"[Teacher] Ack received from CN for counter={msg['ack_counter']} (rn={msg.get('rn')}) → ignoring.")
        return

    # Handle control commands
    if "command" in msg:
        handle_command(msg)
        return

    # Handle violation
    if "rn" in msg and "counter" in msg:
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
