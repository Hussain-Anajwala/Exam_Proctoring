# run_demo.py
import xmlrpc.client
import random
import time
from dataset import STUDENTS

SERVER = "http://localhost:8000"   # change to processor IP:port for multi-machine run
proxy = xmlrpc.client.ServerProxy(SERVER, allow_none=True)

rolls = [r for r, _ in STUDENTS]

print("=== Demo: 20 automated requests (reads/writes) ===")
for i in range(20):
    if random.random() < 0.7:
        rn = random.choice(rolls)
        resp = proxy.student_read(rn)
        print(f"[Demo] READ {rn} -> {resp}")
    else:
        rn = random.choice(rolls)
        new_mse = random.randint(0, 20)
        new_ese = random.randint(0, 40)
        resp = proxy.teacher_update(rn, new_mse, new_ese)
        print(f"[Demo] WRITE {rn} -> mse={new_mse}, ese={new_ese} -> {resp}")
    time.sleep(0.35)

print("\n=== Final snapshots (replicas) ===")
snap = proxy.get_snapshots()
for repl, chunks in snap.items():
    print(f"--- {repl} ---")
    for cname, rows in chunks.items():
        for r in rows:
            print(f"{cname} | {r['rn']} | {r['name']} | ISA={r['isa']} MSE={r['mse']} ESE={r['ese']} TOTAL={r['total']}")
    print()
