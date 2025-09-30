# processor.py
# Processor (Coordinator) - XML-RPC server. Run on main machine.
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from collections import deque
import threading, time, argparse
from dataset import generate_marks, chunkify

# CONFIG
CHUNK_SIZE = 7
REPLICATION_FACTOR = 2 # This is implicitly handled by the chunk_map pattern
MACHINE_NAMES = ["R1", "R2", "R3"]

# ---- Processor (coordinator) ----
class Processor:
    def __init__(self, host="0.0.0.0", port=8000, seed=42):
        self.host = host
        self.port = port

        # Define replica server locations
        self.replica_urls = {
            "R1": "http://localhost:8001",
            "R2": "http://localhost:8002",
            "R3": "http://localhost:8003",
        }

        # Create RPC proxies to connect to replica servers
        self.replica_proxies = {
            name: xmlrpc.client.ServerProxy(url, allow_none=True)
            for name, url in self.replica_urls.items()
        }
        print("[Processor] Connecting to replica servers...")

        # create dataset and chunks
        rows = generate_marks(seed=seed)
        self.chunks = chunkify(rows, CHUNK_SIZE)   # list of lists

        # placement: deterministic round-robin pattern
        self.chunk_map = {}
        pattern = [(MACHINE_NAMES[0], MACHINE_NAMES[1]),
                   (MACHINE_NAMES[1], MACHINE_NAMES[2]),
                   (MACHINE_NAMES[2], MACHINE_NAMES[0])]
        for cid in range(len(self.chunks)):
            self.chunk_map[cid] = list(pattern[cid % 3])

        # load chunks into replicas via RPC
        print("[Processor] Loading initial data into replicas...")
        for cid, chunk in enumerate(self.chunks):
            for rname in self.chunk_map[cid]:
                try:
                    self.replica_proxies[rname].load_chunk(cid, chunk)
                except ConnectionRefusedError:
                    print(f"FATAL: Connection to {rname} ({self.replica_urls[rname]}) failed. Is the replica server running?")
                    exit(1)
        print("[Processor] Data loading complete.")

        # per-chunk state: writer flag, lock, queues
        self.chunk_state = {}
        for cid in range(len(self.chunks)):
            self.chunk_state[cid] = {
                "writer": False,
                "lock": threading.Lock(),
                "read_queue": deque(),
                "write_queue": deque()
            }

        # setup XML-RPC server
        self.server = SimpleXMLRPCServer((self.host, self.port), allow_none=True, logRequests=False)
        self.server.register_function(self.student_read, "student_read")
        self.server.register_function(self.teacher_update, "teacher_update")
        self.server.register_function(self.get_metadata, "get_metadata")
        self.server.register_function(self.get_snapshots, "get_snapshots")

        print(f"[Processor] Coordinator initialized on {self.host}:{self.port}")
        print("[Processor] chunk -> replicas mapping:")
        for cid, rlist in self.chunk_map.items():
            print(f"  Chunk{cid} -> {rlist}")

    def _locate(self, rn):
        for cid, chunk in enumerate(self.chunks):
            for r in chunk:
                if r["rn"] == rn:
                    return cid, r
        return None, None

    # RPC: student read
    def student_read(self, rn):
        cid, _ = self._locate(rn)
        if cid is None:
            return {"status": "ERROR", "msg": f"{rn} not found."}

        state = self.chunk_state[cid]
        with state["lock"]:
            if state["writer"]:
                state["read_queue"].append(rn)
                return {"status": "QUEUED", "msg": f"Read for {rn} queued (chunk {cid} locked)."}
            # safe to read; read from first replica via RPC
            for rname in self.chunk_map[cid]:
                rec = self.replica_proxies[rname].read(cid, rn)
                if rec:
                    return {"status": "OK", "record": rec, "replica": rname}
            return {"status": "ERROR", "msg": f"{rn} not found on replicas."}

    # RPC: teacher update
    def teacher_update(self, rn, new_mse, new_ese):
        cid, _ = self._locate(rn)
        if cid is None:
            return {"status": "ERROR", "msg": f"{rn} not found."}

        state = self.chunk_state[cid]
        with state["lock"]:
            if state["writer"]:
                state["write_queue"].append((rn, new_mse, new_ese))
                return {"status": "QUEUED", "msg": f"Write for {rn} queued (chunk {cid} busy)."}
            state["writer"] = True

        # do prepare on replicas via RPC
        repls = self.chunk_map[cid]
        prepared = []
        for rname in repls:
            ok = self.replica_proxies[rname].prepare(cid, rn, {"mse": new_mse, "ese": new_ese})
            if not ok:
                for p in prepared:
                    self.replica_proxies[p].abort(cid, rn) # Abort via RPC
                with state["lock"]:
                    state["writer"] = False
                return {"status": "ERROR", "msg": f"Prepare failed on {rname}. Aborted."}
            prepared.append(rname)

        # commit on replicas via RPC
        for rname in repls:
            self.replica_proxies[rname].commit(cid, rn)

        # small replication delay
        time.sleep(0.25)

        # release writer and drain queues
        with state["lock"]:
            state["writer"] = False
            # serve queued reads first
            if state["read_queue"]:
                queued = list(state["read_queue"])
                state["read_queue"].clear()
                for qrn in queued:
                    rec = self.replica_proxies[self.chunk_map[cid][0]].read(cid, qrn)
                    print(f"[Processor] Served queued read for {qrn} from {self.chunk_map[cid][0]} -> {rec}")
            # if queued writes exist, start a worker to process first
            if state["write_queue"]:
                nxt = state["write_queue"].popleft()
                threading.Thread(target=self._process_queued_write, args=(cid, nxt), daemon=True).start()

        return {"status": "OK", "msg": f"Write committed for {rn} on {repls}", "replicas": repls}

    def _process_queued_write(self, cid, write_tuple):
        # This function works largely the same, but all replica interactions are RPCs
        rn, mse, ese = write_tuple
        state = self.chunk_state[cid]
        with state["lock"]:
            if state["writer"]:
                state["write_queue"].append((rn, mse, ese))
                return
            state["writer"] = True
        try:
            repls = self.chunk_map[cid]
            prepared = []
            for rname in repls:
                ok = self.replica_proxies[rname].prepare(cid, rn, {"mse": mse, "ese": ese})
                if not ok:
                    for p in prepared:
                        self.replica_proxies[p].abort(cid, rn)
                    with state["lock"]:
                        state["writer"] = False
                    print(f"[Processor] Queued write prepare failed for {rn} on {rname}")
                    return
                prepared.append(rname)
            for rname in repls:
                self.replica_proxies[rname].commit(cid, rn)
            time.sleep(0.25)
            print(f"[Processor] Queued write committed for {rn} on {repls}")
        finally:
            with state["lock"]:
                state["writer"] = False
                if state["read_queue"]:
                    queued = list(state["read_queue"])
                    state["read_queue"].clear()
                    for qrn in queued:
                        rec = self.replica_proxies[self.chunk_map[cid][0]].read(cid, qrn)
                        print(f"[Processor] Served queued read for {qrn} after queued write -> {rec}")
                if state["write_queue"]:
                    nxt = state["write_queue"].popleft()
                    threading.Thread(target=self._process_queued_write, args=(cid, nxt), daemon=True).start()

    def get_metadata(self):
        out = {}
        for cid in range(len(self.chunks)):
            out[f"Chunk{cid}"] = {
                "replicas": list(self.chunk_map[cid]),
                "writer": self.chunk_state[cid]["writer"],
                "queued_reads": len(self.chunk_state[cid]["read_queue"]),
                "queued_writes": len(self.chunk_state[cid]["write_queue"])
            }
        return out

    def get_snapshots(self):
        snap = {}
        for rname, proxy in self.replica_proxies.items():
            # Get chunks from each replica via RPC
            snap[rname] = proxy.get_chunks()
        return snap

    def serve_forever(self):
        self.server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    proc = Processor(host=args.host, port=args.port, seed=args.seed)
    print("[Processor] Ready. Start clients pointing at this server.")
    proc.serve_forever()