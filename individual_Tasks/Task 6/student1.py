import socket
import threading
import time
import sys
import os
sys.path.append(r"C:\Users\Saish\Documents\Github\Exam-System")
from utils import send_json, recv_json

HOST = "127.0.0.1"
MY_PORT = 9002      # student1 listens on 9002
PROCESSOR_PORT = 9000

STUDENT_ID = "student1"

answers = []

def send_to_processor(msg):
    """Send JSON message to processor, retry if processor not ready."""
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PROCESSOR_PORT))
                send_json(s, msg)
            break
        except ConnectionRefusedError:
            print(f"[{STUDENT_ID}] Processor not ready, retrying in 1s...")
            time.sleep(1)

def listen_processor():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow quick restart
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
            print("[Exam Started! Answer the MCQs (A/B/C/D)]")
            for i, q in enumerate(qs):
                print(f"Q{i+1}: {q['q']}")
                for opt in q['options']:
                    print("   ", opt)
                ans = input("Your answer: ").strip().upper()
                answers.append(ans)
            # Submit after input
            send_to_processor({"type": "submit_exam", "student_id": STUDENT_ID, "answers": answers})
        elif msg_type == "submission_status":
            print(f"[{STUDENT_ID}] Submission: {msg.get('status')}")
        elif msg_type == "marks_released":
            print(f"[{STUDENT_ID}] Marks released: {msg.get('marks')}")

if __name__ == "__main__":
    # start listener thread
    threading.Thread(target=listen_processor, daemon=True).start()
    time.sleep(1)

    # retry sending start_exam until processor is ready
    send_to_processor({"type": "start_exam", "student_id": STUDENT_ID})

    # keep alive
    while True:
        time.sleep(1)
