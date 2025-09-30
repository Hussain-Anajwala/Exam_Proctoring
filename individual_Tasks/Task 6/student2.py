import socket
import threading
import time
import sys
import os
sys.path.append(r"C:\Users\Saish\Documents\Github\Exam-System")
from utils import send_json, recv_json

HOST = "127.0.0.1"
MY_PORT = 9003        # student2 listens on port 9003
PROCESSOR_PORT = 9000

STUDENT_ID = "student2"
answers = []

def send_to_processor(msg):
    """Send JSON message to processor."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PROCESSOR_PORT))
        send_json(s, msg)

def listen_processor():
    """Listen for messages from processor."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, MY_PORT))
    server_sock.listen()
    print(f"[{STUDENT_ID}] Listening on port {MY_PORT} for processor messages")
    while True:
        conn, addr = server_sock.accept()
        msg = recv_json(conn)
        conn.close()
        if not msg:
            continue
        msg_type = msg.get("type")

        if msg_type == "questions":
            qs = msg.get("questions", [])
            print("[Exam Started! Answer the MCQs (A/B/C/D)]\n")
            for i, q in enumerate(qs):
                print(f"Q{i+1}: {q['q']}")
                for opt in q['options']:
                    print("   ", opt)
                ans = input("Your answer: ").strip().upper()
                answers.append(ans)
            # Submit answers to processor
            send_to_processor({"type": "submit_exam", "student_id": STUDENT_ID, "answers": answers})

        elif msg_type == "submission_status":
            print(f"[{STUDENT_ID}] Submission: {msg.get('status')}")

        elif msg_type == "marks_released":
            print(f"[{STUDENT_ID}] Marks released: {msg.get('marks')}")
            break

if __name__ == "__main__":
    # Start listener thread
    threading.Thread(target=listen_processor, daemon=True).start()
    time.sleep(1)

    # Request exam from processor
    send_to_processor({"type": "start_exam", "student_id": STUDENT_ID})

    # Keep main thread alive
    while True:
        time.sleep(1)
