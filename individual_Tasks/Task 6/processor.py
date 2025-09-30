import socket
import threading
import time
import sys
import os
sys.path.append(r"C:\Users\Saish\Documents\Github\Exam-System")
from utils import send_json, recv_json

HOST = "127.0.0.1"
PORT = 9000  # processor port

QUESTIONS = [
    {"q": "Which feature is NOT typically associated with distributed systems?",
     "options": ["A) Transparency", "B) Scalability", "C) Centralized control", "D) Fault tolerance"], "ans": "C"},
    {"q": "In which model do processors form a common pool assigned to tasks as needed?",
     "options": ["A) Workstation model", "B) Minicomputer model", "C) Processor pool model", "D) Hybrid model"], "ans": "C"},
    {"q": "Middleware mainly provides which functionality in distributed systems?",
     "options": ["A) Communication and coordination", "B) File system management", "C) Operating system scheduling", "D) Hardware virtualization"], "ans": "A"},
    {"q": "Which of these is an API style often used in middleware systems?",
     "options": ["A) REST", "B) SMTP", "C) POP3", "D) Telnet"], "ans": "A"},
    {"q": "Which technology is widely used for Remote Procedure Calls (RPCs)?",
     "options": ["A) HTTP", "B) gRPC", "C) FTP", "D) SMTP"], "ans": "B"},
    {"q": "Which of the following can lead to RPC failure?",
     "options": ["A) Lost messages", "B) Server crash", "C) Network issues", "D) All of the above"], "ans": "D"},
    {"q": "Which of the following is an example of message-oriented middleware?",
     "options": ["A) Kafka", "B) JDBC", "C) CORBA", "D) RMI"], "ans": "A"},
    {"q": "What is the job of a message broker in distributed systems?",
     "options": ["A) Routing and delivering messages", "B) Encrypting communication", "C) Allocating CPU resources", "D) Managing memory"], "ans": "A"},
    {"q": "Which algorithm is commonly used for logical clock synchronization?",
     "options": ["A) Ricart-Agrawala", "B) Bully algorithm", "C) Lamport's logical clocks", "D) Token ring"], "ans": "C"},
    {"q": "Which mutual exclusion method uses a circulating token?",
     "options": ["A) Centralized approach", "B) Ricart-Agrawala", "C) Lamport’s algorithm", "D) Token-based method"], "ans": "D"},
]

status_db = {}      # student_id → status
submission_db = {}  # student_id → {"answers": [], "marks": int, "released": bool}
lock = threading.Lock()

# Mapping student IDs and teacher to ports
STUDENT_PORTS = {"student1": 9002, "student2": 9003, "teacher": 9001}

def handle_client(conn, addr):
    try:
        msg = recv_json(conn)
        if not msg:
            return
        student_id = msg.get("student_id")
        if not student_id:
            return
        msg_type = msg.get("type")

        if msg_type == "start_exam":
            status_db[student_id] = "Exam started"
            send_to_student(student_id, {"type": "questions", "questions": QUESTIONS})

        elif msg_type == "submit_exam":
            with lock:
                if student_id in submission_db:
                    send_to_student(student_id, {"type": "submission_status", "status": "already_submitted"})
                    return
                answers = msg.get("answers", [])
                marks = sum(1 for i, q in enumerate(QUESTIONS)
                            if i < len(answers) and answers[i].upper() == q["ans"])
                submission_db[student_id] = {"answers": answers, "marks": marks, "released": False}
                status_db[student_id] = "Exam submitted"
                
                # Notify student
                send_to_student(student_id, {"type": "submission_status", "status": "accepted", "marks": marks})
                # Notify teacher
                send_to_student("teacher", {"type": "status", "student_id": student_id, "status": "Exam submitted"})

        elif msg_type == "get_status":
            status = status_db.get(student_id, "No status")
            send_to_student(student_id, {"type": "status", "status": status})

        elif msg_type == "release_marks":
            if student_id in submission_db:
                submission_db[student_id]["released"] = True
                status_db[student_id] = "Marks released"
                
                # Notify student
                send_to_student(student_id, {"type": "marks_released", "marks": submission_db[student_id]["marks"]})
                # Notify teacher
                send_to_student("teacher", {"type": "marks_released", "student_id": student_id, "marks": submission_db[student_id]["marks"]})

    except Exception as e:
        print(f"[Processor] Error: {e}")

def send_to_student(student_id, msg):
    port = STUDENT_PORTS.get(student_id)
    if not port:
        print(f"[Processor] Unknown recipient: {student_id}")
        return
    # Retry loop if recipient not ready yet
    for attempt in range(5):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, port))
                send_json(s, msg)
            return
        except ConnectionRefusedError:
            print(f"[Processor] {student_id} not ready yet, retrying...")
            time.sleep(1)
        except Exception as e:
            print(f"[Processor] Could not send to {student_id}: {e}")

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    print(f"[Processor] Listening on {HOST}:{PORT}...")

    while True:
        try:
            conn, addr = server_sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("[Processor] Shutting down...")
            server_sock.close()
            break

if __name__ == "__main__":
    main()
