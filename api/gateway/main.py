from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
import time
from api.search.search_router import router as search_router
from api.product.import_file import router as product_import_router
from api.product.template import router as product_template_router

app = FastAPI(
    title="E-Commerce Search API",
    description="API for intent-based product search and management",
    version="1.0.0",
    openapi_tags=[  # NEW: Add tags for Swagger organization
        {
            "name": "search",
            "description": "Product search operations"
        },
        {
            "name": "products",
            "description": "Product management operations"
        }
    ]
)

app.include_router(search_router, prefix="/api/v1", tags=["search"])  # UPDATED
app.include_router(product_import_router, prefix="/api/v1", tags=["products"])  # NEW
app.include_router(product_template_router, prefix="/api/v1", tags=["products"])

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms")
    return response

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )