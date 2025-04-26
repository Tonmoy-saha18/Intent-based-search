from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi import Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.limiter import limiter
from fastapi import FastAPI, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta
from app.core.security import get_current_admin_user
from app.core.monitoring import tracer, api_request_counter, api_latency_histogram
import time

from app.services.product_service import insert_bulk_product, insert_one_product, get_all_product, find_product
from app.schemas.product import ProductIn, ProductOut

router = APIRouter()

# Apply different rate limits to different endpoints
@router.post("/import")
@limiter.limit("10/minute")  # 10 requests per minute
async def import_product(request: Request, product: ProductIn):
    await insert_one_product(product)

@router.get("/")
async def get_all_products(
    request: Request,
    current_user: dict = Depends(get_current_admin_user)  # Requires admin role
):
    return await get_all_product()

@router.post("/import/csv", response_model=dict)
@limiter.limit("5/minute")  # 5 requests per minute (since file uploads are heavier)
async def import_products_csv(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    result = await insert_bulk_product(file)
    return {"message": f"{len(result.inserted_ids)} products imported successfully"}

# @router.post("/search/")
# @limiter.limit("5/minute")  # 5 requests per minute
# async def search(request: Request, query: str, rank: int):
#     results = await find_product(query, rank)
#     return {"results": results}

@router.post("/search/")
@limiter.limit("5/minute")
async def search(request: Request, query: str, rank=10):
    start_time = time.time()
    
    with tracer.start_as_current_span("search_endpoint"):
        results = await find_product(query, rank)
        
    api_request_counter.add(1, {"endpoint": "search"})
    api_latency_histogram.record(time.time() - start_time, {"endpoint": "search"})
    
    return {"results": results}

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}