import os
import socket
import time
from fastapi import FastAPI
from pydantic import BaseModel
from hazelcast import HazelcastClient

app = FastAPI()

HZ_MEMBERS = os.getenv("HAZELCAST_MEMBERS", "hazelcast-service:5701")
instance_id = socket.gethostname()

client = HazelcastClient(cluster_members=[HZ_MEMBERS])
transactions_map = client.get_map("transactions").blocking()

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: int
    timestamp: str

@app.post("/log")
def log_transaction(tx: dict):
    print(tx)
    tx_id = tx.get("transaction_id", str(time.time()))
    tx["processed_by"] = instance_id
    
    transactions_map.put(tx_id, tx)
    return {"status": "logged", "pod": instance_id}

@app.get("/logs/{user_id}")
def get_logs(user_id: str):
    all_values = transactions_map.values()
    return [t for t in all_values if t["user_id"] == user_id]