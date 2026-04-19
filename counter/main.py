from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, select
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import threading
import hazelcast
import httpx
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://counter_user:counter_pass@postgres:5432/counter_db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    user_id = Column(String, primary_key=True)
    balance = Column(Integer, default=0)

Base.metadata.create_all(engine)

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: int

def save_to_db(tx_data: dict):
    db = SessionLocal()
    try:
        user_id = tx_data.get("user_id")
        amount = tx_data.get("amount")
        
        result = db.execute(
            select(Account).where(Account.user_id == user_id).with_for_update()
        )
        account = result.scalar_one_or_none()
        
        if account is None:
            account = Account(user_id=user_id, balance=amount)
            db.add(account)
        else:
            account.balance += amount
        
        db.commit()
        db.refresh(account)
        print(f" [DB] Updated {user_id}: new balance {account.balance}")
        return account.balance
    except Exception as e:
        db.rollback()
        print(f" [DB ERROR] {e}")
        return None
    finally:
        db.close()

def consume_queue():
    try:
        hz_client = hazelcast.HazelcastClient(cluster_members=["hazelcast:5701"])
        queue = hz_client.get_queue("counter_queue").blocking()
        print(queue)
        print(" [MQ] Consumer started, waiting for messages...")

        while True:
            tx_data = queue.take()
            print(f" [MQ] Received transaction for user: {tx_data.get('user_id')}")
            save_to_db(tx_data)
    except Exception as e:
        print(f" [MQ ERROR] Consumer crashed: {e}")



@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=consume_queue, daemon=True)
    thread.start()

    async with httpx.AsyncClient() as client:
        try:
            await client.post("http://config-server:8888/register?service_name=counter")
            print(" [REG] Registered with Config Server")
        except Exception as e:
            print(f" [REG ERROR] Registration failed: {e}")
    yield

app = FastAPI(lifespan=lifespan)



@app.post("/update")
def update_balance(tx: Transaction):
    """Manual update endpoint (still works for testing)"""
    balance = save_to_db(tx.dict())
    if balance is None:
        raise HTTPException(status_code=500, detail="Database update failed")
    return {"balance": balance}

@app.get("/user/{user_id}")
def get_balance(user_id: str):
    db = SessionLocal()
    try:
        result = db.execute(select(Account).where(Account.user_id == user_id))
        account = result.scalar_one_or_none()
        return {"balance": account.balance if account else 0}
    finally:
        db.close()

@app.get("/accounts")
def get_all():
    db = SessionLocal()
    try:
        result = db.execute(select(Account))
        accounts = result.scalars().all()
        return {acc.user_id: acc.balance for acc in accounts}
    finally:
        db.close()
