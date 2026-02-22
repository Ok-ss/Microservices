# get_accounts_10clients_1user.py
import requests
from concurrent.futures import ThreadPoolExecutor
import time

URL = "http://localhost:8000/accounts"
CLIENTS = 10
REQUESTS_PER_CLIENT = 1000

def worker(_):
    for _ in range(REQUESTS_PER_CLIENT):
        requests.get(URL)

start = time.time()
with ThreadPoolExecutor(max_workers=CLIENTS) as executor:
    for i in range(CLIENTS):
        executor.submit(worker, i)
end = time.time()

total_requests = CLIENTS * REQUESTS_PER_CLIENT
print("Total time:", end - start)
print("Requests/sec:", total_requests / (end - start))
