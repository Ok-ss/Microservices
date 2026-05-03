import requests
import time
from concurrent.futures import ThreadPoolExecutor

URL = "http://192.168.49.2:30001/send" # Update with your Actual IP
CLIENTS = 10
REQ_PER_CLIENT = 1000
TARGET_USER = "user0"

def worker(id):
    session = requests.Session()
    m = {"log_ms": 0.0, "queue_ms": 0.0, "ok": 0}
    for _ in range(REQ_PER_CLIENT):
        try:
            r = session.post(URL, json={"user_id": TARGET_USER, "amount": 1}, timeout=5)
            data = r.json()
            m["log_ms"] += data["internal_metrics"]["log_ms"]
            m["queue_ms"] += data["internal_metrics"]["queue_ms"]
            m["ok"] += 1
        except: pass
    return m

start = time.time()
with ThreadPoolExecutor(max_workers=CLIENTS) as ex:
    results = list(ex.map(worker, range(CLIENTS)))
end = time.time()

total_t = end - start
total_log = sum(r["log_ms"] for r in results) / 1000
total_q = sum(r["queue_ms"] for r in results) / 1000

print(f"Total Time: {total_t:.2f}s")
print(f"Logging Service Calls: {total_log/CLIENTS:.2f}s ({(total_log/total_t/CLIENTS)*100:.1f}%)")
print(f"Counter (Queue) Calls: {total_q:.2f}s ({(total_q/total_t)*100:.1f}%)")