import csv
import io

from fastapi import HTTPException, File

from app.db.mongo import get_product_collection
from app.schemas.product import ProductIn


async def insert_bulk_product(file: File(...)):
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    products = []
    for row in reader:
        try:
            product = ProductIn(
                name=row["name"],
                description=row.get("description"),
                category=row["category"],
                brand=row.get("brand"),
                price=float(row["price"]),
                stock=int(row["stock"]),
                tags=row.get("tags", "").split(";") if row.get("tags") else []
            )
            products.append(product.dict())
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid data row: {row}. Error: {str(e)}")

    collection = get_product_collection()
    result = await collection.insert_many(products)
    return result


async def insert_one_product(product: ProductIn):
    collection = get_product_collection()
    result = await collection.insert_one(product.dict())
    if result.inserted_id:
        return {"message": "Product imported", "id": str(result.inserted_id)}
    raise HTTPException(status_code=500, detail="Failed to insert product")


async def get_all_product():
    collection = get_product_collection()
    products_cursor = collection.find()
    products = []
    async for product in products_cursor:
        product["id"] = str(product["_id"])
        del product["_id"]
        products.append(product)
    return products
