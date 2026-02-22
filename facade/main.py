# facade/main.py

from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import time
import uuid

app = FastAPI()

log_time_total = 0
counter_time_total = 0

transactions_time_total = 0
balances_time_total = 0

all_accounts_time_total = 0

class ClientTransaction(BaseModel):
    user_id: str
    amount: int

@app.post("/send")
async def send_transaction(data: ClientTransaction):

    global log_time_total, counter_time_total

    tx = {
        "timestamp": str(time.time()),
        "user_id": data.user_id,
        "amount": data.amount,
    }

    async with httpx.AsyncClient() as client:

        start = time.perf_counter()
        await client.post("http://logging:8000/log", json=tx)
        log_time_total += time.perf_counter() - start

        start = time.perf_counter()
        response = await client.post("http://counter:8000/update", json=tx)
        counter_time_total += time.perf_counter() - start

    return {
        "transaction_id": tx["timestamp"],
        "balance": response.json()["balance"]
    }

@app.get("/user/{user_id}")
async def get_user_data(user_id: str):
    global transactions_time_total, balances_time_total

    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        transactions_resp = await client.get(f"http://logging:8000/logs/{user_id}")
        transactions_time_total += time.perf_counter() - start

        start = time.perf_counter()
        balance_resp = await client.get(f"http://counter:8000/user/{user_id}")
        balances_time_total += time.perf_counter() - start

    return {
        "balance": balance_resp.json()["balance"],
        "transactions": transactions_resp.json()  # just the list
    }

@app.get("/accounts")
async def get_all_accounts():
    """
    Fetch balances of all clients from counter-service
    """
    global all_accounts_time_total
    
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        response = await client.get("http://counter:8000/accounts")
        all_accounts_time_total += time.perf_counter() - start


    # counter-service already returns a dict like {"user1": 100, "user2": 50}
    return response.json()

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
