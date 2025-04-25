from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File
from app.schemas.product import ProductIn, ProductOut
from app.db.mongo import get_product_collection
import csv
import io

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

@router.post("/import/csv", response_model=dict)
async def import_products_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

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
    return {"message": f"{len(result.inserted_ids)} products imported successfully"}
