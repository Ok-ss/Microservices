# random_10clients_1user.py
import requests
from concurrent.futures import ThreadPoolExecutor
import time
import random

BASE_URL = "http://localhost:8000"
CLIENTS = 10
REQUESTS_PER_CLIENT = 1000
USER = "user0"

def worker(_):
    for _ in range(REQUESTS_PER_CLIENT):
        choice = random.choice(["post", "get_user", "get_accounts"])
        if choice == "post":
            requests.post(f"{BASE_URL}/send", json={"user_id": USER, "amount": 1})
        elif choice == "get_user":
            requests.get(f"{BASE_URL}/user/{USER}")
        else:
            requests.get(f"{BASE_URL}/accounts")

start = time.time()
with ThreadPoolExecutor(max_workers=CLIENTS) as executor:
    for i in range(CLIENTS):
        executor.submit(worker, i)
end = time.time()

total_requests = CLIENTS * REQUESTS_PER_CLIENT
print("Total time:", end - start)
print("Requests/sec:", total_requests / (end - start))
