"""
AI News Hub — FastAPI Backend
Serves multilingual news articles from MongoDB Atlas.
"""

import os
from datetime import datetime, timezone
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, DESCENDING

load_dotenv()

# ────────────────────────── App Setup ──────────────────────────

app = FastAPI(
    title="AI News Hub API",
    description="Multilingual news articles powered by Gemini AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────── MongoDB ──────────────────────────

MONGO_URI = os.environ.get("MONGO_URI", "")
if not MONGO_URI:
    print("⚠️  MONGO_URI not set — running without database connection.")
    db = None
    collection = None
else:
    client = MongoClient(MONGO_URI)
    db = client["newsdb"]
    collection = db["articles"]
    # Create indexes for performance
    collection.create_index([("published", DESCENDING)])
    collection.create_index("category")
    collection.create_index("id", unique=True)
    print("✅ Connected to MongoDB Atlas")


# ────────────────────────── Helpers ──────────────────────────

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document for JSON response."""
    doc["_id"] = str(doc["_id"])
    return doc


# ────────────────────────── Routes ──────────────────────────

@app.get("/")
async def root():
    return {
        "service": "AI News Hub API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/ping")
async def ping():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/articles")
async def get_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    lang: Optional[str] = Query(None, description="Language code (hi/en/mr)"),
    limit: int = Query(50, ge=1, le=100, description="Max articles to return"),
):
    """Fetch articles with optional category and language filters."""
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not configured")

    query = {}
    if category and category != "all":
        query["category"] = category

    # If lang specified, only return articles that have content in that language
    if lang:
        query[f"content.{lang}"] = {"$exists": True}

    cursor = collection.find(query).sort("published", DESCENDING).limit(limit)
    articles = [serialize_doc(doc) for doc in cursor]
    return articles


@app.get("/articles/{article_id}")
async def get_article(article_id: str):
    """Fetch a single article by its id."""
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not configured")

    doc = collection.find_one({"id": article_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Article not found")
    return serialize_doc(doc)


@app.post("/articles")
async def create_article(article: dict):
    """
    Create a new article. Expected JSON body:
    {
        "id": "unique_id",
        "category": "politics|sports|entertainment|local|jobs",
        "content": {
            "hi": {"title": "...", "body": "..."},
            "en": {"title": "...", "body": "..."},
            "mr": {"title": "...", "body": "..."}
        }
    }
    """
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not configured")

    # Validate required fields
    if "id" not in article:
        raise HTTPException(status_code=422, detail="Missing 'id' field")
    if "content" not in article:
        raise HTTPException(status_code=422, detail="Missing 'content' field")
    if "category" not in article:
        raise HTTPException(status_code=422, detail="Missing 'category' field")

    # Check for duplicate
    existing = collection.find_one({"id": article["id"]})
    if existing:
        return {"status": "duplicate", "message": f"Article {article['id']} already exists"}

    # Set published timestamp if not provided
    if "published" not in article:
        article["published"] = datetime.now(timezone.utc).isoformat()

    collection.insert_one(article)
    return {"status": "created", "id": article["id"]}


@app.delete("/articles/{article_id}")
async def delete_article(article_id: str):
    """Delete an article by its id."""
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not configured")

    result = collection.delete_one({"id": article_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"status": "deleted", "id": article_id}


# ────────────────────────── Entrypoint ──────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
