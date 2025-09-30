import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 8000

teacher_conn = None
student_conns = {}  # id → conn
lock = threading.Lock()

def handle_teacher(conn, addr):
    global teacher_conn
    teacher_conn = conn
    print(f"[Server] Registered teacher at {addr}")

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            if data.strip() == "sync":
                start_berkeley_sync()
        except:
            break

def handle_student(conn, addr, student_id):
    with lock:
        student_conns[student_id] = conn
    print(f"[Server] Registered student{student_id} at {addr}")

def start_berkeley_sync():
    print("[Server] Starting Berkeley sync...")

    # Step 1: Ask each student for their local time
    times = {}
    for sid, conn in student_conns.items():
        conn.sendall("time_request".encode())
        t = conn.recv(1024).decode().strip()
        print(f"[Server] Got time from Student{sid}: {t}")
        h, m, s = map(int, t.split(":"))
        times[sid] = h * 3600 + m * 60 + s

    # Step 2: Add teacher’s own clock
    teacher_conn.sendall("time_request".encode())
    t = teacher_conn.recv(1024).decode().strip()
    print(f"[Server] Got time from Teacher: {t}")
    h, m, s = map(int, t.split(":"))
    times["teacher"] = h * 3600 + m * 60 + s

    # Step 3: Compute average offset
    avg_time = sum(times.values()) // len(times)
    print(f"[Server] Average system time (sec): {avg_time}")

    # Step 4: Send adjustments to everyone
    for sid, conn in student_conns.items():
        offset = avg_time - times[sid]
        conn.sendall(f"adjust:{offset}".encode())

    teacher_offset = avg_time - times["teacher"]
    teacher_conn.sendall(f"adjust:{teacher_offset}".encode())

    print("[Server] Synchronization complete.")

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    print(f"[Server] Listening on {HOST}:{PORT}")

    student_id = 1
    while True:
        conn, addr = server_sock.accept()
        role = conn.recv(1024).decode().strip()
        if role == "teacher":
            threading.Thread(target=handle_teacher, args=(conn, addr), daemon=True).start()
        elif role == "student":
            threading.Thread(target=handle_student, args=(conn, addr, student_id), daemon=True).start()
            student_id += 1

if __name__ == "__main__":
    main()
