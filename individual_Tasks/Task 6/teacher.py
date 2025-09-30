import socket
import threading
import time
import sys
import os
sys.path.append(r"C:\Users\Saish\Documents\Github\Exam-System")
from utils import send_json, recv_json

HOST = "127.0.0.1"
TEACHER_PORT = 9001  # teacher listens here
PROCESSOR_PORT = 9000
STUDENT_IDS = ["student1", "student2"]

# store which students have been released
released = set()

def send_to_processor(msg):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PROCESSOR_PORT))
            send_json(s, msg)
    except Exception as e:
        print(f"[Teacher] Could not send to processor: {e}")

def listen_processor():
    """Listen for processor messages about status or marks."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, TEACHER_PORT))
    server_sock.listen()
    print(f"[Teacher] Listening on port {TEACHER_PORT} for processor messages")

    while True:
        conn, addr = server_sock.accept()
        msg = recv_json(conn)
        conn.close()
        if not msg:
            continue
        msg_type = msg.get("type")
        student_id = msg.get("student_id")

        if msg_type == "status":
            status = msg.get("status")
            print(f"[Teacher] Status of {student_id}: {status}")
            if status == "Exam submitted" and student_id not in released:
                # automatically release marks
                print(f"[Teacher] Releasing marks for {student_id}")
                send_to_processor({"type": "release_marks", "student_id": student_id})
                released.add(student_id)

        elif msg_type == "marks_released":
            marks = msg.get("marks")
            print(f"[Teacher] Marks released for {student_id}: {marks}")

def poll_students():
    """Periodically ask processor for student status"""
    while len(released) < len(STUDENT_IDS):
        for student_id in STUDENT_IDS:
            if student_id in released:
                continue
            # ask processor for status
            send_to_processor({"type": "get_status", "student_id": student_id})
        time.sleep(2)
    print("[Teacher] Marks released for all students.")

if __name__ == "__main__":
    # start listener thread
    threading.Thread(target=listen_processor, daemon=True).start()
    time.sleep(1)

    # start polling students
    poll_students()
