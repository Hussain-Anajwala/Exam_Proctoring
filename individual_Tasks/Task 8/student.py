# student.py
import xmlrpc.client
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--server", default="http://localhost:8000", help="processor URL (http://IP:port)")
parser.add_argument("--rn", default=None, help="roll to read")
args = parser.parse_args()

proxy = xmlrpc.client.ServerProxy(args.server, allow_none=True)

if args.rn:
    rn = args.rn
else:
    rn = input("Enter roll number to read: ").strip()

res = proxy.student_read(rn)
if isinstance(res, dict):
    if res.get("status") == "OK":
        print(f"[Student] Read OK from {res.get('replica')}: {res.get('record')}")
    else:
        print(f"[Student] {res.get('status')}: {res.get('msg')}")
else:
    print("[Student] Unexpected response:", res)
