# counter/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from threading import Lock

app = FastAPI()

balances: Dict[str, int] = {}
lock = Lock()

class Transaction(BaseModel):
    timestamp: str
    user_id: str
    amount: int

@app.post("/update")
def update_balance(tx: Transaction):
    with lock:
        balances[tx.user_id] = balances.get(tx.user_id, 0) + tx.amount
        return {"balance": balances[tx.user_id]}

@app.get("/user/{user_id}")
def get_balance(user_id: str):
    return {"balance": balances.get(user_id, 0)}

@app.get("/accounts")
def get_all():
    return balances
