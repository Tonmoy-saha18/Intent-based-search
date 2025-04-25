from fastapi import FastAPI
from app.api.v1.product import router as product_router

app = FastAPI(title="Ecommerce site")

app.include_router(product_router, prefix="/api/v1/products", tags=["Products"])
