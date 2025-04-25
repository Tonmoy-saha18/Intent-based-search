from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: Optional[str] = None


class ProductOut(ProductCreate):
    id: int