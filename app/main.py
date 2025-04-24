from fastapi import FastAPI, HTTPException
from app.schemas import ProductCreate, ProductOut
from elastic import index_product_es, get_product_es, create_index
from app.vector_store import index_product_vector

app = FastAPI()

@app.on_event("startup")
def startup():
    create_index()

@app.post("/products", response_model=ProductOut)
def create_product(product: ProductCreate):
    # Simulate product ID generation (you'd use a UUID or a better ID in real systems)
    from uuid import uuid4
    product_id = int(uuid4().int >> 64)

    # Convert to dict
    data = product.dict()
    data["id"] = product_id

    # Index in Elasticsearch
    index_product_es(product_id, data)

    # Index in FAISS
    index_product_vector(product_id, product.description)
    index_product_vector(product_id, product.name)
    index_product_vector(product_id, product.category)

    return ProductOut(id=product_id, **product.dict())

@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int):
    product = get_product_es(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product