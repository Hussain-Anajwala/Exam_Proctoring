# teacher.py
import socket
import threading
import time
import sys
import os
sys.path.append(r"C:\Users\Saish\Documents\Github\Exam-System")
from utils import send_json, recv_json

HOST = "127.0.0.1"
PORT = 5000

# Store connected client sockets keyed by role
clients = {}   # e.g. {"CN": socket, "CD": socket}
clients_lock = threading.Lock()

students = {
    58: "Hussain", 59: "Saish", 65: "Khushal", 75: "Hasnain", 68: "Amritesh"
}

# marksheet and violation tracking
marksheet = {r: 100 for r in students}
violations = {r: 0 for r in students}

def safe_send(role, data):
    """
    Send JSON to a connected client role if present.
    """
    with clients_lock:
        sock = clients.get(role)
    if sock:
        try:
            send_json(sock, data)
        except Exception:
            print(f"[Teacher] failed to send to {role}")

def handle_violation_msg(msg):
    roll = msg.get("roll")
    question_no = msg.get("question_no", -1)
    counter = msg.get("counter")  # CN supplies counter
    if roll not in violations:
        print(f"[Teacher] Unknown roll {roll} received, ignoring.")
        return
    violations[roll] += 1
    vcount = violations[roll]

    if vcount == 1:
        marksheet[roll] = 50
        status = "noted"
    elif vcount == 2:
        marksheet[roll] = 0
        status = "terminate"
    else:
        print(f"[Teacher] Roll {roll} already terminated → ignoring.")
        return

    print(f"[Teacher] Violation {vcount} for roll {roll} on Q{question_no}, percentage={marksheet[roll]}")

    # Reply to CN (must include the same counter so CN can match)
    reply = {
        "counter": counter,
        "roll": roll,
        "violation": vcount,
        "question_no": question_no,
        "percentage": marksheet[roll],
        "status": status
    }
    safe_send("CN", reply)

def handle_command(msg):
    cmd = msg.get("command")
    if cmd == "send_marks":
        print("[Teacher] Preparing final marksheet...")
        # convert keys to strings (to mimic original json structure)
        report = {"command": "marks_report", "marks": {str(k): v for k, v in marksheet.items()}}
        # send to CN and CD if connected
        safe_send("CN", report)
        safe_send("CD", report)
        print("[Teacher] Marks report sent to CN and CD.")
    elif cmd == "marks_report_ack":
        print("[Teacher] Marks report acknowledged by peer.")
    else:
        # other / unknown commands
        print(f"[Teacher] Unknown command received: {cmd}")

def handle_client(sock: socket.socket, addr):
    """
    Thread per connected client (CN or CD).
    The first message from client must declare role: {"role":"CN"} or {"role":"CD"}.
    After that, the client sends regular messages.
    """
    try:
        # The initial role declaration is already read by accept loop and used. But in case not:
        # We'll just loop reading incoming messages.
        while True:
            msg = recv_json(sock)
            if not msg:
                break
            # Process message
            # Accept messages that are either violations (with "roll" & "question_no") or commands
            if "roll" in msg and "question_no" in msg:
                handle_violation_msg(msg)
            elif "command" in msg:
                handle_command(msg)
            elif "ack_counter" in msg:
                # ack from CN for a previously sent teacher->CN message (if any)
                print(f"[Teacher] Ack received from CN for counter={msg.get('ack_counter')} (roll={msg.get('roll')})")
            else:
                print(f"[Teacher] Received unknown message: {msg}")
    finally:
        # Remove this client from clients dict (if present)
        with clients_lock:
            for role, csock in list(clients.items()):
                if csock == sock:
                    print(f"[Teacher] {role} disconnected.")
                    del clients[role]
        try:
            sock.close()
        except:
            pass

def accept_loop(server_sock):
    while True:
        sock, addr = server_sock.accept()
        # Read the initial role declaration (non-blocking expectation)
        role_msg = recv_json(sock)
        role = None
        if isinstance(role_msg, dict) and "role" in role_msg:
            role = role_msg["role"]
        else:
            # If client didn't send role, we try to keep going; but mark role by address
            role = f"unknown_{addr}"
        with clients_lock:
            clients[role] = sock
        print(f"[Teacher] {role} connected from {addr}")
        threading.Thread(target=handle_client, args=(sock, addr), daemon=True).start()

def main():
    print("[Teacher] Starting Teacher server on %s:%s..." % (HOST, PORT))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    try:
        accept_loop(server)
    except KeyboardInterrupt:
        print("\n[Teacher] Shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    main()
