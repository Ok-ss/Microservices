from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import time
import uuid
import random
import httpx
import hazelcast

app = FastAPI()

log_time_total = 0
counter_time_total = 0

transactions_time_total = 0
balances_time_total = 0

all_accounts_time_total = 0

class ClientTransaction(BaseModel):
    user_id: str
    amount: int

hz_client = hazelcast.HazelcastClient(cluster_members=["hazelcast:5701"])
queue = hz_client.get_queue("counter_queue").blocking()
print(queue)

async def get_service_url(service_name: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://config-server:8888/nodes/{service_name}")
        ips = resp.json()
        if not ips:
            raise Exception(f"No instances of {service_name} found")
        selected_ip = random.choice(ips)
        return f"http://{selected_ip}:8000"

@app.post("/send")
async def send_transaction(data: ClientTransaction):
    tx = {
        "transaction_id": str(uuid.uuid4()),
        "user_id": data.user_id,
        "amount": data.amount,
    }
    
    log_url = await get_service_url("logging")
    async with httpx.AsyncClient() as client:
        await client.post(f"{log_url}/log", json=tx)

    queue.put(tx) 

    return {"status": "Transaction queued", "transaction_id": tx["transaction_id"]}


@app.get("/user/{user_id}")
async def get_user_data(user_id: str):
    global transactions_time_total, balances_time_total
    transactions = []
    balance = None 

    async with httpx.AsyncClient() as client:
        try:
            log_url = await get_service_url("logging")
            start = time.perf_counter()
            transactions_resp = await client.get(f"{log_url}/logs/{user_id}", timeout=2.0)
            transactions = transactions_resp.json()
            transactions_time_total += time.perf_counter() - start
        except Exception as e:
            print(f"Logging service error: {e}")
            transactions = []

        try:
            counter_url = await get_service_url("counter")
            start = time.perf_counter()
            balance_resp = await client.get(f"{counter_url}/user/{user_id}", timeout=2.0)
            balance = balance_resp.json().get("balance")
            balances_time_total += time.perf_counter() - start
        except Exception as e:
            print(f"Counter service unreachable: {e}")
            balance = None

    return {
        "balance": balance,
        "transactions": transactions
    }

@app.get("/accounts")
async def get_all_accounts():
    global all_accounts_time_total

    try:
        counter_url = await get_service_url("counter")
        async with httpx.AsyncClient() as client:
            start = time.perf_counter()
            response = await client.get(f"{counter_url}/accounts", timeout=5.0)
            all_accounts_time_total += time.perf_counter() - start
            return response.json()
    except Exception as e:
        print(f"Failed to fetch accounts: {e}")
        return {}


@app.get("/metrics")
def metrics():
    return {
        "POST":{
        "logging_service_time": log_time_total,
        "counter_service_time": counter_time_total
        },"GET (1 user)":{
        "logging_service_time": transactions_time_total,
        "counter_service_time": balances_time_total
        }, "GET (all accounts)":{
        "counter_service_time": all_accounts_time_total
        }
    }

@app.post("/metrics/reset")
def reset():
    global log_time_total, counter_time_total, transactions_time_total, balances_time_total, all_accounts_time_total
    log_time_total = 0
    counter_time_total = 0
    transactions_time_total = 0
    balances_time_total = 0
    all_accounts_time_total = 0
    return {"status": "reset"}
