import socket
import time
import sys
import os
sys.path.append(r"C:\Users\Saish\Documents\Github\Exam-System")
from utils import send_json, recv_json

HOST = "127.0.0.1"
MY_PORT = 5002       # s2 listens on port 5002
TEACHER_PORT = 5000  # teacher listens on port 5000

me = "s2"
student_id = "S2"
timestamp = 2

def send_to_teacher(msg):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, TEACHER_PORT))
        send_json(s, msg)

def wait_for_grant():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, MY_PORT))
    server_sock.listen()
    print(f"[{student_id}] Listening for grants on port {MY_PORT}")

    while True:
        conn, addr = server_sock.accept()
        msg = recv_json(conn)
        conn.close()
        if msg and msg.get("type") == "grant" and msg.get("to") == student_id:
            print(f"[{student_id}] ✅ Granted CS → entering critical section")
            time.sleep(3)  # simulate critical section
            send_to_teacher({"type": "release", "from": student_id})
            print(f"[{student_id}] 🔓 Released CS")
            break

if __name__ == "__main__":
    print(f"[{student_id}] Starting...")
    send_to_teacher({"type": "request", "from": student_id, "timestamp": timestamp})
    print(f"[{student_id}] Sent request to Teacher")
    wait_for_grant()
