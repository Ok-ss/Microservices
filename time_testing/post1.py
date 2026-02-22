# post_10clients_1user.py
import requests
from concurrent.futures import ThreadPoolExecutor
import time

URL = "http://localhost:8000/send"
CLIENTS = 10
REQUESTS_PER_CLIENT = 1000
USER = "user0"

def worker(_):
    for _ in range(REQUESTS_PER_CLIENT):
        requests.post(URL, json={"user_id": USER, "amount": 1})

start = time.time()
with ThreadPoolExecutor(max_workers=CLIENTS) as executor:
    for i in range(CLIENTS):
        executor.submit(worker, i)
end = time.time()

total_requests = CLIENTS * REQUESTS_PER_CLIENT
print("Total time:", end - start)
print("Requests/sec:", total_requests / (end - start))
