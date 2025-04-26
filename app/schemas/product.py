from typing import List, Optional
from pydantic import BaseModel, Field


class ProductVariant(BaseModel):
    color: Optional[str]
    size: Optional[str]
    price: float
    stock: int


class ProductImage(BaseModel):
    url: str
    alt_text: Optional[str] = None


class ProductIn(BaseModel):
    name: str = Field(..., example="Nike Air Max 270")
    description: Optional[str] = Field(None, example="Breathable, lightweight running shoes.")
    category: str = Field(..., example="Footwear")
    brand: Optional[str] = Field(None, example="Nike")
    price: float = Field(..., example=149.99)
    lan: str


class ProductOut(ProductIn):
    id: str
