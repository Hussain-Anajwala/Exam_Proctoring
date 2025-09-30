#!/usr/bin/env python3
"""
Main Server (Load Balancer via Migration) - Final, race-free version
- Ensures BATCH_END is sent only once per exam batch
- Centralizes socket closing in notify_all_clients_submitted
- Synchronizes per-client sends with per-client locks to avoid WinError 10038
"""

import socket
import threading
import queue
import json
import logging
import time

# ---------------- Config ----------------
HOST = "127.0.0.1"       # localhost
PORT = 5000              # Main server port for clients
BACKUP_HOST = "127.0.0.1" # Backup server host (localhost)
BACKUP_PORT = 5001
TOTAL_STUDENTS = 15
BUFFER_LIMIT = 10
MIGRATE_THRESHOLD = int(BUFFER_LIMIT * 0.8)
LOCAL_WORKERS = BUFFER_LIMIT
PROCESS_TIME_SEC = 2

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | MAIN | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("main_server.log"),
        logging.StreamHandler()
    ],
)

# ---------------- Shared State ----------------
# client_sockets maps student_id -> {"sock": socket, "lock": threading.Lock(), "closed": bool}
client_sockets_lock = threading.Lock()
client_sockets = {}
recv_count_lock = threading.Lock()
received_count = 0
local_inflight_lock = threading.Lock()
local_inflight = 0
local_queue = queue.Queue(maxsize=BUFFER_LIMIT)
local_done = set()
forwarded_ids_lock = threading.Lock()
forwarded_ids = []
backup_ack_event = threading.Event()
backup_done_set = set()
batch_done_event = threading.Event()
batch_end_sent = threading.Event()   # ensure only one BATCH_END

# ---------------- Helpers ----------------
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


def send_to_backup(message):
    with socket.create_connection((BACKUP_HOST, BACKUP_PORT), timeout=10) as bsock:
        send_json(bsock, message)
        try:
            return recv_json(bsock, timeout=10)
        except:
            return None


def notify_backup_batch_end(batch_id="default"):
    msg = {"type": "BATCH_END", "batch_id": batch_id}
    logging.info("Notifying backup: BATCH_END")
    send_to_backup(msg)

# ---------------- Local Processing ----------------
def worker_local():
    global local_inflight
    while True:
        item = local_queue.get()
        if item is None:
            break
        student_id, payload = item
        logging.info(f"Local processing started for {student_id}")
        time.sleep(PROCESS_TIME_SEC)
        with local_inflight_lock:
            local_inflight -= 1
        local_done.add(student_id)
        logging.info(f"Local processing done for {student_id}")
        local_queue.task_done()
        maybe_finalize_batch()


def maybe_finalize_batch():
    with recv_count_lock:
        all_received = (received_count >= TOTAL_STUDENTS)
    with local_inflight_lock:
        local_complete = (local_inflight == 0 and local_queue.unfinished_tasks == 0)
    backup_complete = backup_ack_event.is_set()
    if all_received and local_complete and backup_complete and not batch_done_event.is_set():
        logging.info("Batch conditions met: notifying all clients...")
        notify_all_clients_submitted()
        batch_done_event.set()


def notify_all_clients_submitted():
    # Copy keys to avoid holding lock while we do network IO
    with client_sockets_lock:
        targets = list(client_sockets.items())

    for sid, info in targets:
        csock = info.get("sock")
        lock = info.get("lock")
        if csock is None or lock is None:
            # unexpected, skip
            continue

        # Use per-client lock to synchronize with handler which may be sending the immediate ACK
        try:
            with lock:
                # If already marked closed by someone else, skip
                if info.get("closed"):
                    continue
                try:
                    send_json(csock, {"type": "SUBMITTED", "student_id": sid, "status": "OK"})
                except Exception:
                    # client may have disconnected; we'll still try to close silently
                    pass
                info["closed"] = True
                # Safe shutdown/close wrapper
                try:
                    csock.shutdown(socket.SHUT_WR)
                except Exception:
                    pass
                try:
                    csock.close()
                except Exception:
                    pass
                logging.info(f"Notified client {sid} -> SUBMITTED")
        except Exception as e:
            logging.error(f"Error while notifying {sid}: {e}")
        finally:
            # Remove entry from the central map to free memory
            with client_sockets_lock:
                client_sockets.pop(sid, None)

# ---------------- Networking ----------------
def handle_client(conn, addr):
    global received_count, local_inflight
    student_id = None
    lock = threading.Lock()
    try:
        msg = recv_json(conn, timeout=15)
        if msg.get("type") != "SUBMIT":
            raise ValueError("Unexpected message")

        student_id = msg["student_id"]
        payload = msg.get("payload", {})
        logging.info(f"Received SUBMIT from {student_id}")

        # Register client socket with its own lock and closed flag
        with client_sockets_lock:
            client_sockets[student_id] = {"sock": conn, "lock": lock, "closed": False}

        # Update count
        with recv_count_lock:
            received_count += 1
            rc = received_count
        logging.info(f"Received count = {rc}/{TOTAL_STUDENTS}")

        # Send BATCH_END only once after last student
        if rc >= TOTAL_STUDENTS and not batch_end_sent.is_set():
            notify_backup_batch_end()
            batch_end_sent.set()

        # Decide local vs migrate; ensure ack is done under the same per-client lock
        with local_inflight_lock:
            current_inflight = local_inflight

        if current_inflight >= MIGRATE_THRESHOLD:
            with forwarded_ids_lock:
                forwarded_ids.append(student_id)
            fmsg = {"type": "FORWARD", "student_id": student_id, "payload": payload}
            logging.info(f"Migrating {student_id} to backup")
            # forwarding may block briefly; that's OK
            send_to_backup(fmsg)
            # Send immediate RECEIVED under lock unless socket already closed
            with lock:
                info = client_sockets.get(student_id)
                if info and not info.get("closed"):
                    try:
                        send_json(conn, {"type": "RECEIVED", "via": "backup", "student_id": student_id})
                    except Exception:
                        # client may be gone; mark closed and continue
                        info["closed"] = True
        else:
            # try to enqueue for local processing
            enqueued = False
            with local_inflight_lock:
                if local_inflight < BUFFER_LIMIT:
                    local_inflight += 1
                    local_queue.put((student_id, payload))
                    enqueued = True
            # Send immediate RECEIVED under lock unless socket already closed
            with lock:
                info = client_sockets.get(student_id)
                if info and not info.get("closed"):
                    try:
                        if enqueued:
                            send_json(conn, {"type": "RECEIVED", "via": "main", "student_id": student_id})
                        else:
                            # Shouldn't reach here often; fallback to migration
                            send_json(conn, {"type": "RECEIVED", "via": "backup", "student_id": student_id})
                    except Exception:
                        info["closed"] = True

    except Exception as e:
        # Don't close the socket here; notify_all_clients_submitted is the only place that closes sockets.
        logging.error(f"Client handler error: {e}")
    finally:
        # handler thread exits; socket remains managed by client_sockets until final notification
        pass


def backup_listener():
    listen_port = BACKUP_PORT + 10
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, listen_port))
    srv.listen(5)
    logging.info(f"Listening for backup acks at {HOST}:{listen_port}")
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_backup_control, args=(conn, addr), daemon=True).start()


def handle_backup_control(conn, addr):
    try:
        msg = recv_json(conn, timeout=10)
        if msg.get("type") == "BATCH_OK":
            ids = msg.get("student_ids", [])
            backup_done_set.update(ids)
            logging.info(f"Received BATCH_OK for {len(ids)} students.")
            backup_ack_event.set()
            send_json(conn, {"type": "ACK"})
            maybe_finalize_batch()
    except Exception as e:
        logging.error(f"Backup control error: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def client_listener():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(100)
    logging.info(f"Main Server listening on {HOST}:{PORT}")

    # Start local workers
    for _ in range(LOCAL_WORKERS):
        threading.Thread(target=worker_local, daemon=True).start()
    # Start backup control listener
    threading.Thread(target=backup_listener, daemon=True).start()

    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    logging.info("Main Server starting...")
    client_listener()
