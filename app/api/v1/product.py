from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.core.product_service import insert_bulk_product, insert_one_product, get_all_product
from app.schemas.product import ProductIn, ProductOut

router = APIRouter()


@router.post("/import")
async def import_product(product: ProductIn):
    await insert_one_product(product)


@router.get("/", response_model=List[ProductOut])
async def get_all_products():
    return await get_all_product()


@router.post("/import/csv", response_model=dict)
async def import_products_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    result = await insert_bulk_product(file)
    return {"message": f"{len(result.inserted_ids)} products imported successfully"}
