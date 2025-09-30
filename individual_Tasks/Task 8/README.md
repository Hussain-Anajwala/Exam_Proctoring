How to run (quick)

On processor machine:

python processor.py --host 0.0.0.0 --port 8000 --seed 42


(If running on a remote machine, set --host 0.0.0.0 and note its IP.)

On any client machine (student/teacher/demo), point to processor IP:

Single student read:

python student.py --server http://<PROCESSOR_IP>:8000 --rn 23102A0058


Single teacher update:

python teacher.py --server http://<PROCESSOR_IP>:8000 --rn 23102A0058 --mse 18 --ese 32


Demo (automated requests — runs 20 requests and prints results):

Edit SERVER variable in run_demo.py to match http://<PROCESSOR_IP>:8000, or run with environment change.

python run_demo.py


Notes

Ports: ensure port 8000 is allowed on Processor machine firewall.

This setup simulates replicas in-process inside processor.py (R1/R2/R3). If you later want real replica processes on separate machines (true distributed 2PC), I can extend the design so each replica runs its own XML-RPC server and processor.py calls prepare/commit/abort on them remotely.

student_read returns "QUEUED" if the read was queued because a write was active — queued reads are served automatically by the processor and logged in its console.