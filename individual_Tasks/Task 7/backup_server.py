#!/usr/bin/env python3
"""
Backup Server
- Receives forwarded submissions from Main Server.
- Processes them and sends BATCH_OK when done.
"""

import socket
import threading
import json
import time
import logging

# ---------------- Config ----------------
HOST = "127.0.0.1"   # Run on localhost
PORT = 5001          # Backup server port
PROCESS_TIME_SEC = 2 # Simulated grading time per submission

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | BACKUP | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("backup_server.log"),
        logging.StreamHandler()
    ],
)

# ---------------- State ----------------
batch_data = []
batch_lock = threading.Lock()

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

def handle_client(conn, addr):
    try:
        msg = recv_json(conn, timeout=10)
        mtype = msg.get("type")

        if mtype == "FORWARD":
            sid = msg["student_id"]
            logging.info(f"Received FORWARD submission {sid}")
            with batch_lock:
                batch_data.append(sid)
            # simulate grading
            time.sleep(PROCESS_TIME_SEC)
            send_json(conn, {"type": "ACK", "student_id": sid})

        elif mtype == "BATCH_END":
            logging.info("Received BATCH_END, sending BATCH_OK to main server...")
            # connect to main control channel
            with socket.create_connection(("127.0.0.1", PORT + 10), timeout=10) as msock:
                send_json(msock, {"type": "BATCH_OK", "student_ids": batch_data})
                ack = recv_json(msock, timeout=10)
                logging.info(f"Main responded: {ack}")
            send_json(conn, {"type": "ACK"})

        else:
            logging.warning(f"Unexpected message: {msg}")
            send_json(conn, {"type": "NACK"})

    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        conn.close()

def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(50)
    logging.info(f"Backup Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
