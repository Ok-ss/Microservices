# logging/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List
import hazelcast
import socket

app = FastAPI()

# Hazelcast client
client = hazelcast.HazelcastClient(
    cluster_members=["hazelcast:5701"]
)
transactions_map = client.get_map("transactions").blocking()

instance_id = socket.gethostname()

class Transaction(BaseModel):
    transaction_id: str
    timestamp: str
    user_id: str
    amount: int

@app.post("/log")
def log_transaction(tx: Transaction):
    tx_dict = tx.dict()
    tx_dict["instance_id"] = instance_id
    # put_if_absent is atomic in Hazelcast, so thread-safe.
    existing = transactions_map.put_if_absent(tx.transaction_id, tx_dict)
    if existing is not None:
        return {"status": "duplicate"}
    return {"status": "stored"}

@app.get("/logs/{user_id}")
def get_user_logs(user_id: str):
    all_txs = transactions_map.values()
    return [
        tx for tx in all_txs
        if tx["user_id"] == user_id
    ]
