import os
import threading
import hazelcast
import time
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, String, Integer, select
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres-service:5432/microservices_db")
HZ_MEMBERS = os.getenv("HAZELCAST_MEMBERS", "hazelcast-service:5701")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    user_id = Column(String, primary_key=True)
    balance = Column(Integer, default=0)

Base.metadata.create_all(engine)

def save_to_db_with_retry(tx_data, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        db = SessionLocal()
        try:
            user_id = tx_data["user_id"]
            amount = tx_data["amount"]
            
            acc = db.query(Account).with_for_update().filter_by(user_id=user_id).first()
            
            if not acc:
                acc = Account(user_id=user_id, balance=amount)
                db.add(acc)
            else:
                acc.balance += amount
            
            db.commit()
            return True 
        except OperationalError:
            db.rollback()
            attempt += 1
            time.sleep(0.05 * attempt)
        except Exception as e:
            db.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            db.close()
    return False

def consume_queue():
    hz_client = hazelcast.HazelcastClient(cluster_members=[HZ_MEMBERS])
    queue = hz_client.get_queue("counter_queue").blocking()
    while True:
        tx_data = queue.take()
        save_to_db_with_retry(tx_data)

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=consume_queue, daemon=True)
    thread.start()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/user/{user_id}")
def get_balance(user_id: str):
    db = SessionLocal()
    acc = db.query(Account).filter_by(user_id=user_id).first()
    return {"balance": acc.balance if acc else 0}

@app.get("/accounts")
def get_all():
    db = SessionLocal()
    accounts = db.query(Account).all()
    return {a.user_id: a.balance for a in accounts}