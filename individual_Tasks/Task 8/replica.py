# replica.py
# A standalone XML-RPC server for a single replica.
from xmlrpc.server import SimpleXMLRPCServer
import argparse
import copy

class Replica:
    def __init__(self, name):
        self.name = name
        self.chunks = {}            # chunk_id -> list of records
        self.prepare_buffer = {}    # (chunk_id, rn) -> pending fields
        print(f"[{self.name}] Replica object created.")

    def load_chunk(self, chunk_id, rows):
        """RPC: Coordinator sends a chunk of data to this replica."""
        self.chunks[chunk_id] = [copy.deepcopy(r) for r in rows]
        print(f"[{self.name}] Loaded Chunk{chunk_id} with {len(rows)} records.")
        return True

    def read(self, chunk_id, rn):
        """RPC: Read a record from a specific chunk."""
        rows = self.chunks.get(chunk_id)
        if not rows:
            return None
        for r in rows:
            if r["rn"] == rn:
                print(f"[{self.name}] Served read for {rn} from Chunk{chunk_id}.")
                return r.copy()
        return None

    def prepare(self, chunk_id, rn, fields):
        """RPC: 2PC Prepare Phase."""
        if chunk_id not in self.chunks:
            return False
        for r in self.chunks[chunk_id]:
            if r["rn"] == rn:
                self.prepare_buffer[(chunk_id, rn)] = fields.copy()
                print(f"[{self.name}] Prepared write for {rn} in Chunk{chunk_id}.")
                return True
        return False

    def commit(self, chunk_id, rn):
        """RPC: 2PC Commit Phase."""
        key = (chunk_id, rn)
        if key not in self.prepare_buffer:
            return False
        fields = self.prepare_buffer.pop(key)
        for r in self.chunks[chunk_id]:
            if r["rn"] == rn:
                if "mse" in fields: r["mse"] = fields["mse"]
                if "ese" in fields: r["ese"] = fields["ese"]
                r["total"] = r["isa"] + r["mse"] + r["ese"]
                print(f"[{self.name}] Committed write for {rn} in Chunk{chunk_id}.")
                return True
        return False

    def abort(self, chunk_id, rn):
        """RPC: 2PC Abort Phase."""
        self.prepare_buffer.pop((chunk_id, rn), None)
        print(f"[{self.name}] Aborted write for {rn} in Chunk{chunk_id}.")
        return True

    def get_chunks(self):
        """RPC: For getting final snapshots. Convert integer keys to strings for XML-RPC compatibility."""
        # This converts keys like 0, 1, 2 into strings like "Chunk0", "Chunk1", "Chunk2"
        return {f"Chunk{cid}": rows for cid, rows in self.chunks.items()}
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Replica name (e.g., R1)")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()

    server = SimpleXMLRPCServer((args.host, args.port), allow_none=True, logRequests=True)
    print(f"[{args.name}] Replica server listening on http://{args.host}:{args.port}")
    server.register_instance(Replica(args.name))
    server.serve_forever()