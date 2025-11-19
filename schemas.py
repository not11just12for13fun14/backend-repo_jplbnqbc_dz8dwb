"""
Database Schemas for PECULIAR MASTERPIECE

Each Pydantic model represents a MongoDB collection. Collection name is the lowercase of the class name.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    slug: str = Field(..., description="URL-friendly slug")
    description: str = Field("", description="Rich description")
    price: float = Field(..., ge=0)
    original_price: Optional[float] = Field(None, ge=0)
    categories: List[str] = Field(default_factory=list)
    collections: List[str] = Field(default_factory=list)
    rarity: Literal["common","limited","ultra","grail"] = Field("limited")
    total_edition: Optional[int] = Field(None, ge=1)
    images: List[str] = Field(default_factory=list, description="Image URLs")
    colors: List[str] = Field(default_factory=list)
    sizes: List[str] = Field(default_factory=list)
    in_stock: bool = True
    inventory: dict = Field(default_factory=lambda: {"S":10,"M":10,"L":10,"XL":10})
    rating: dict = Field(default_factory=lambda: {"average":0.0,"count":0})
    featured: bool = False
    created_at: Optional[datetime] = None

class Review(BaseModel):
    product_id: str
    name: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = ""
    photo_url: Optional[str] = None

class WishlistItem(BaseModel):
    client_id: str
    product_id: str
    color: Optional[str] = None
    size: Optional[str] = None

class CartItem(BaseModel):
    client_id: str
    product_id: str
    quantity: int = Field(1, ge=1)
    color: Optional[str] = None
    size: Optional[str] = None

class Subscriber(BaseModel):
    email: str
    ref: Optional[str] = None

class SaleEvent(BaseModel):
    product_title: str
    city: str
    seconds_ago: int

