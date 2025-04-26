from fastapi import FastAPI
from app.api.v1.product import router as product_router
from app.db.qrdant import init_collection

app = FastAPI(title="Ecommerce site")


@app.on_event("startup")
async def startup_event():
    init_collection()


app.include_router(product_router, prefix="/api/v1/products", tags=["Products"])
