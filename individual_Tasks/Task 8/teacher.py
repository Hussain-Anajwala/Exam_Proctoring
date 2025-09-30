# teacher.py
import xmlrpc.client
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--server", default="http://localhost:8000", help="processor URL (http://IP:port)")
parser.add_argument("--rn", default=None, help="roll to update")
parser.add_argument("--mse", type=int, default=None)
parser.add_argument("--ese", type=int, default=None)
args = parser.parse_args()

proxy = xmlrpc.client.ServerProxy(args.server, allow_none=True)

if args.rn is None:
    rn = input("Enter roll number to update: ").strip()
else:
    rn = args.rn

if args.mse is None:
    mse = int(input("Enter new MSE (0-20): ").strip())
else:
    mse = args.mse

if args.ese is None:
    ese = int(input("Enter new ESE (0-40): ").strip())
else:
    ese = args.ese

res = proxy.teacher_update(rn, mse, ese)
print("[Teacher] Response:", res)
