# counter/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os

app = FastAPI()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://counter_user:counter_pass@localhost:5432/counter_db")
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
    timestamp: str
    user_id: str
    amount: int

@app.post("/update")
def update_balance(tx: Transaction):
    db = SessionLocal()
    try:
        # SELECT FOR UPDATE locks the row during transaction.
        # This prevents concurrent updates from causing lost writes.
        result = db.execute(
            select(Account).where(Account.user_id == tx.user_id).with_for_update()
        )
        account = result.scalar_one_or_none()
        
        if account is None:
            # Create new account if it doesn't exist
            account = Account(user_id=tx.user_id, balance=tx.amount)
            db.add(account)
        else:
            account.balance += tx.amount
        
        db.commit()
        db.refresh(account)
        return {"balance": account.balance}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

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
