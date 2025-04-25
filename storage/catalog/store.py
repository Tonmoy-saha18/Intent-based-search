from pymongo import MongoClient
from typing import List, Dict, Optional
import os
import logging
from bson.decimal128 import Decimal128
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)


class ProductStore:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.client = MongoClient(mongo_uri)
        self.db = self.client["ecommerce"]
        self.products = self.db["products"]
        self._create_indexes()

    def _create_indexes(self):
        self.products.create_index("product_id", unique=True)
        self.products.create_index("category")
        self.products.create_index("price")
        self.products.create_index("last_updated")

    def bulk_get(self, product_ids: List[str]) -> List[Dict]:
        try:
            cursor = self.products.find({"product_id": {"$in": product_ids}})
            products = []

            for doc in cursor:
                # Convert MongoDB document to dict
                product = {
                    "product_id": doc["product_id"],
                    "title": doc["title"],
                    "description": doc.get("description", ""),
                    "category": doc["category"],
                    "price": float(doc["price"].to_decimal()) if isinstance(doc["price"], Decimal128) else float(
                        doc["price"]),
                    "attributes": doc.get("attributes", {}),
                    "rating": doc.get("rating", {}).get("average", 0),
                    "review_count": doc.get("rating", {}).get("count", 0),
                    "vector": doc.get("vector", []),
                    "sponsored": doc.get("sponsored", False)
                }
                products.append(product)

            return products
        except Exception as e:
            logger.error(f"Failed to fetch products: {str(e)}")
            raise

    def update_product(self, product_id: str, update_data: Dict):
        try:
            # Convert float to Decimal128 for price
            if "price" in update_data:
                update_data["price"] = Decimal128(str(update_data["price"]))

            self.products.update_one(
                {"product_id": product_id},
                {"$set": update_data},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {str(e)}")
            raise


def get_product_store():
    return ProductStore()