from fastapi import FastAPI, Request
from app.api.v1.product import router as product_router
from app.db.qrdant import init_collection
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import make_asgi_app

# Initialize the limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Ecommerce site")

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Store the limiter in the app state
app.state.limiter = limiter

# Add Prometheus metrics route
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Exception handler must be defined before including routers
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
        headers={"Retry-After": "60"}
    )

@app.on_event("startup")
async def startup_event():
    init_collection()

app.include_router(product_router, prefix="/api/v1/products", tags=["Products"])