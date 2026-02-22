# load_test.py

import requests
import time
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost:8000/send"

CLIENTS = 10
REQUESTS_PER_CLIENT = 10000

def worker(user):
    for _ in range(REQUESTS_PER_CLIENT):
        requests.post(URL, json={"user_id": user, "amount": 1})

start = time.time()

with ThreadPoolExecutor(max_workers=CLIENTS) as executor:
    for i in range(CLIENTS):
        executor.submit(worker, f"user{i}")

end = time.time()

total_requests = CLIENTS * REQUESTS_PER_CLIENT
total_time = end - start

print("Total time:", total_time)
print("Requests/sec:", total_requests / total_time)
