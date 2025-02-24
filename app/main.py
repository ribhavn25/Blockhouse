from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import databases
import sqlalchemy

DATABASE_URL = "sqlite:///./test.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("symbol", sqlalchemy.String),
    sqlalchemy.Column("price", sqlalchemy.Float),
    sqlalchemy.Column("quantity", sqlalchemy.Integer),
    sqlalchemy.Column("order_type", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

app = FastAPI()

class OrderIn(BaseModel):
    symbol: str
    price: float
    quantity: int
    order_type: str

class Order(BaseModel):
    id: int
    symbol: str
    price: float
    quantity: int
    order_type: str

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/orders", response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(**order.dict())
    last_record_id = await database.execute(query)
    return {**order.dict(), "id": last_record_id}

@app.get("/orders", response_model=List[Order])
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)
