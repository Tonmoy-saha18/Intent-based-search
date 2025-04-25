from typing import List

from fastapi import APIRouter, HTTPException
from app.schemas.product import ProductIn, ProductOut
from app.db.mongo import get_product_collection

router = APIRouter()

@router.post("/import")
async def import_product(product: ProductIn):
    collection = get_product_collection()
    result = await collection.insert_one(product.dict())
    if result.inserted_id:
        return {"message": "Product imported", "id": str(result.inserted_id)}
    raise HTTPException(status_code=500, detail="Failed to insert product")

@router.get("/", response_model=List[ProductOut])
async def get_all_products():
    collection = get_product_collection()
    products_cursor = collection.find()
    products = []
    async for product in products_cursor:
        product["id"] = str(product["_id"])
        del product["_id"]
        products.append(product)
    return products
