import os
import uuid
import time
import httpx
import hazelcast
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

LOGGING_URL = os.getenv("LOGGING_SERVICE_URL", "http://logging-service:8000")
COUNTER_URL = os.getenv("COUNTER_SERVICE_URL", "http://counter-service:8000")
HZ_MEMBERS = os.getenv("HAZELCAST_MEMBERS", "hazelcast-service:5701")

metrics_data = {
    "log_time": 0.0,
    "counter_time": 0.0,
    "all_accounts_time": 0.0
}

class ClientTransaction(BaseModel):
    user_id: str
    amount: int

hz_client = hazelcast.HazelcastClient(cluster_members=[HZ_MEMBERS])
queue = hz_client.get_queue("counter_queue").blocking()

@app.post("/send")
async def send_transaction(data: ClientTransaction):
    tx_id = str(uuid.uuid4())
    tx = {
        "transaction_id": tx_id, 
        "user_id": data.user_id, 
        "amount": data.amount, 
        "timestamp": str(time.time())
    }
    
    start_log = time.perf_counter()
    async with httpx.AsyncClient() as client:
        await client.post(f"{LOGGING_URL}/log", json=tx)
    log_duration = (time.perf_counter() - start_log) * 1000

    start_queue = time.perf_counter()
    queue.put(tx) 
    queue_duration = (time.perf_counter() - start_queue) * 1000

    return {
        "status": "queued",
        "id": tx_id,
        "internal_metrics": {
            "log_ms": log_duration,
            "queue_ms": queue_duration
        }
    }

@app.get("/user/{user_id}")
async def get_user_data(user_id: str):
    async with httpx.AsyncClient() as client:
        log_resp = await client.get(f"{LOGGING_URL}/logs/{user_id}")
        count_resp = await client.get(f"{COUNTER_URL}/user/{user_id}")
        
        return {
            "balance": count_resp.json().get("balance"),
            "transactions": log_resp.json()
        }
    
@app.get("/accounts")
async def get_all_accounts():
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{COUNTER_URL}/accounts", timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            metrics_data["all_accounts_time"] += time.perf_counter() - start
            return data
        except Exception as e:
            return {"error": f"Failed to fetch accounts: {str(e)}"}

@app.get("/metrics")
def get_metrics():
    return metrics_data

@app.post("/metrics/reset")
def reset_metrics():
    for key in metrics_data: metrics_data[key] = 0.0
    return {"status": "reset"}