from __future__ import annotations

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str | None = None


class ProductOut(ProductCreate):
    id: int