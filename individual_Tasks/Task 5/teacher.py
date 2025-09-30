import heapq
import time
import socket
import sys
import os
sys.path.append(r"C:\Users\Saish\Documents\Github\Exam-System")
from utils import send_json, recv_json

# Configuration: teacher listens on port 5000
HOST = "127.0.0.1"
PORT = 5000

request_queue = []
current_holder = "Teacher"

# Mapping students → ports (these must match student scripts)
STUDENT_PORTS = {"s1": 5001, "s2": 5002, "s3": 5003}

def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    print(f"[Teacher] Listening on {HOST}:{PORT}")
    return server_sock

def accept_connections(server_sock):
    while True:
        conn, addr = server_sock.accept()
        msg = recv_json(conn)
        if not msg:
            conn.close()
            continue
        handle_message(msg)
        conn.close()

def handle_message(msg):
    global current_holder
    if msg["type"] == "request":
        student = msg["from"]
        ts = msg["timestamp"]
        print(f"[Teacher] Request from {student} at t={ts}")
        heapq.heappush(request_queue, (ts, student))
        if current_holder == "Teacher":
            ts, student = heapq.heappop(request_queue)
            current_holder = student
            print(f"[Teacher] Granting CS to {student}")
            send_to_student(student, {"type": "grant", "to": student})

    elif msg["type"] == "release":
        student = msg["from"]
        print(f"[Teacher] {student} released CS")
        if request_queue:
            ts, next_student = heapq.heappop(request_queue)
            current_holder = next_student
            print(f"[Teacher] Granting CS to {next_student}")
            send_to_student(next_student, {"type": "grant", "to": next_student})
        else:
            current_holder = "Teacher"
            print("[Teacher] CS returned to Teacher (queue empty)")

def send_to_student(student, msg):
    port = STUDENT_PORTS[student.lower()]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, port))
        send_json(s, msg)

if __name__ == "__main__":
    server = start_server()
    while True:
        accept_connections(server)
