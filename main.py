import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Review, WishlistItem, CartItem, Subscriber, SaleEvent

app = FastAPI(title="PECULIAR MASTERPIECE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class ObjIdModel(BaseModel):
    id: str

def oid(id_str: str):
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")

@app.get("/")
def root():
    return {"name": "PECULIAR MASTERPIECE API", "status": "ok"}

@app.get("/test")
def test_database():
    resp = {
        "backend": "running",
        "database": "unavailable",
        "collections": []
    }
    try:
        _ = db.list_collection_names()
        resp["database"] = "connected"
        resp["collections"] = _
    except Exception as e:
        resp["error"] = str(e)
    return resp

# Seed minimal demo products if none exist (for preview)
@app.post("/seed")
def seed_products():
    if db is None:
        raise HTTPException(500, "Database not configured")
    if db.product.count_documents({}) > 0:
        return {"seeded": False, "count": db.product.count_documents({})}
    demo = [
        Product(
            title="Midnight Iris",
            slug="midnight-iris",
            description="Limited tee with glowing astral iris.",
            price=89.0,
            categories=["tees"],
            collections=["drop-001"],
            rarity="limited",
            total_edition=144,
            images=["/products/midnight-iris-1.jpg"],
            colors=["black","white"],
            sizes=["S","M","L","XL"],
            featured=True,
        ).model_dump(),
        Product(
            title="Void Seraph",
            slug="void-seraph",
            description="Oversized tee with neon seraphic glitch halo.",
            price=109.0,
            categories=["tees"],
            collections=["drop-001"],
            rarity="ultra",
            total_edition=88,
            images=["/products/void-seraph-1.jpg"],
            colors=["black"],
            sizes=["S","M","L","XL"],
            featured=True,
        ).model_dump(),
    ]
    for d in demo:
        create_document("product", d)
    return {"seeded": True, "count": db.product.count_documents({})}

# Products
@app.get("/products")
def list_products(collection: Optional[str] = None, q: Optional[str] = None):
    filt = {}
    if collection:
        filt["collections"] = collection
    if q:
        filt["title"] = {"$regex": q, "$options": "i"}
    prods = get_documents("product", filt)
    for p in prods:
        p["id"] = str(p.pop("_id"))
    return prods

@app.get("/products/{slug}")
def get_product(slug: str):
    p = db.product.find_one({"slug": slug})
    if not p:
        raise HTTPException(404, "Not found")
    p["id"] = str(p.pop("_id"))
    return p

# Wishlist
@app.post("/wishlist")
def add_wishlist(item: WishlistItem):
    create_document("wishlistitem", item)
    return {"ok": True}

# Cart
@app.post("/cart")
def add_cart(item: CartItem):
    create_document("cartitem", item)
    return {"ok": True}

# Reviews
@app.post("/reviews")
def create_review(review: Review):
    create_document("review", review)
    return {"ok": True}

# Newsletter
@app.post("/subscribe")
def subscribe(s: Subscriber):
    create_document("subscriber", s)
    return {"ok": True}

# Sales popups (mock stream)
@app.get("/sales")
def recent_sales(limit: int = 5):
    sample = [
        {"product_title": "Midnight Iris", "city": "Berlin", "seconds_ago": 47},
        {"product_title": "Void Seraph", "city": "Tokyo", "seconds_ago": 92},
        {"product_title": "Neon Oracle", "city": "New York", "seconds_ago": 131},
    ]
    return sample[:limit]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
