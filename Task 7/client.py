#!/usr/bin/env python3
"""
Client Simulator
- Spawns 15 students that submit simultaneously after exam end.
"""

import socket
import threading
import json
import time
import logging

# ---------------- Config ----------------
MAIN_HOST = "127.0.0.1"  # Main server IP (localhost)
MAIN_PORT = 5000
EXAM_DURATION_SEC = 10   # shorter (10s) for quick testing
TOTAL_STUDENTS = 15
START_ROLL = "23102A0050"

def gen_ids(start="23102A0050", n=15):
    prefix = start[:-4]
    base = int(start[-4:])
    for i in range(n):
        yield f"{prefix}{base + i:04d}"

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | CLIENT | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("client.log"),
        logging.StreamHandler()
    ],
)

def send_json(sock, obj):
    data = (json.dumps(obj) + "\n").encode("utf-8")
    sock.sendall(data)

def recv_json(sock, timeout=None):
    sock.settimeout(timeout)
    buf = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Socket closed")
        buf += chunk
        if b"\n" in buf:
            line, rest = buf.split(b"\n", 1)
            return json.loads(line.decode("utf-8"))

def student_thread(student_id, start_barrier):
    try:
        logging.info(f"{student_id} connecting...")
        sock = socket.create_connection((MAIN_HOST, MAIN_PORT), timeout=10)
        start_barrier.wait()
        submit_payload = {"answers_hash": f"hash_of_{student_id}"}
        send_json(sock, {"type": "SUBMIT", "student_id": student_id, "payload": submit_payload})

        try:
            ack = recv_json(sock, timeout=10)
            logging.info(f"{student_id} got ack: {ack}")
        except Exception:
            logging.warning(f"{student_id} didn't get immediate ack")

        final = recv_json(sock, timeout=300)
        logging.info(f"{student_id} FINAL: {final}")
        sock.close()
    except Exception as e:
        logging.error(f"{student_id} error: {e}")

def main():
    logging.info(f"Client starting. {TOTAL_STUDENTS} students will submit in {EXAM_DURATION_SEC}s...")
    ids = list(gen_ids(START_ROLL, TOTAL_STUDENTS))
    start_barrier = threading.Barrier(TOTAL_STUDENTS + 1)
    threads = []
    for sid in ids:
        t = threading.Thread(target=student_thread, args=(sid, start_barrier), daemon=True)
        t.start()
        threads.append(t)
    time.sleep(EXAM_DURATION_SEC)
    logging.info("Exam time over! Releasing students...")
    start_barrier.wait()
    for t in threads:
        t.join()
    logging.info("All students done.")

if __name__ == "__main__":
    main()
