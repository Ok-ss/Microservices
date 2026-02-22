# logging/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

transactions: Dict[str, dict] = {}

class Transaction(BaseModel):
    timestamp: str
    user_id: str
    amount: int

@app.post("/log")
def log_transaction(tx: Transaction):
    if tx.timestamp in transactions:
        return {"status": "duplicate"}

    transactions[tx.timestamp] = tx.dict()
    return {"status": "stored"}

@app.get("/logs/{user_id}")
def get_user_logs(user_id: str):
    return [
        tx for tx in transactions.values()
        if tx["user_id"] == user_id
    ]
