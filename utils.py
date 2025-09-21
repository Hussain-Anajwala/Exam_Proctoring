# utils.py
import json
import socket

def send_json(sock: socket.socket, data: dict):
    """
    Send a JSON-serializable object over TCP with '\n' delimiter.
    """
    msg = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    try:
        sock.sendall(msg + b"\n")
    except Exception as e:
        # Caller handles closed sockets
        raise

def recv_json(sock: socket.socket):
    """
    Receive one JSON object from the socket (terminated by newline).
    Blocks until a full line received or socket closed.
    Returns dict or None if socket closed.
    """
    buffer = b""
    while True:
        try:
            chunk = sock.recv(4096)
        except Exception:
            return None
        if not chunk:
            return None
        buffer += chunk
        if b"\n" in buffer:
            line, rest = buffer.split(b"\n", 1)
            # Put remainder back into socket-like buffer is not necessary for our usage,
            # because we always handle messages one-by-one in a loop and don't need rest.
            try:
                return json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                # if decode fails, skip that line
                continue
