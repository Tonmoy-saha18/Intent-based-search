from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "productdb")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

def get_product_collection():
    return db.get_collection("products")
