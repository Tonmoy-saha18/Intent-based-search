from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
from services.intent.service import classify_intent
from services.embedding.service import get_embedding
from storage.vector.store import VectorStore
from storage.catalog.store import ProductStore
from services.ranking.service import rerank_results
from shared.cache import cache
import json

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    filters: Optional[dict] = None
    user_id: Optional[str] = None


class SearchResponse(BaseModel):
    results: list
    intent: dict
    total: int
    debug: Optional[dict] = None


@router.post("/search", response_model=SearchResponse)
@cache(ttl=60, key_builder=lambda f, *args, **kwargs: f"search:{kwargs['request'].query}")
async def search(
        request: SearchRequest,
        vector_store: VectorStore = Depends(VectorStore),
        product_store: ProductStore = Depends(ProductStore)
):
    # Step 1: Intent classification
    intent = classify_intent(request.query)

    # Step 2: Vector search
    query_vector = get_embedding(request.query)
    product_ids = vector_store.search(
        vector=query_vector,
        k=100,
        filters=request.filters
    )

    # Step 3: Fetch products
    products = product_store.bulk_get(product_ids)

    # Step 4: Re-rank
    ranked = rerank_results(
        products,
        intent=intent,
        user_id=request.user_id
    )

    return {
        "results": ranked[:10],
        "intent": intent,
        "total": len(ranked),
        "debug": {
            "product_ids": product_ids[:5],
            "query_vector": query_vector[:5]  # First 5 dims for debug
        } if request.user_id == "admin" else None
    }