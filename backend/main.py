import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.chroma_client import get_chroma_client, get_image_collection, get_pdf_collection
from backend.ai_models import get_clip, get_sentence_transformer
from backend.api.routes_index import router as index_router
from backend.api.routes_search import router as search_router
from backend.api.routes_preview import router as preview_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    print("[AssetVault] Initializing SQLite database...")
    init_db()
    
    # Initialize ChromaDB collections
    print("[AssetVault] Connecting to ChromaDB collections...")
    get_image_collection()
    get_pdf_collection()
    
    print("[AssetVault] System startup completed.")
    yield
    print("[AssetVault] Shutting down...")

app = FastAPI(
    title="AssetVault - AI DAM System API",
    description="Multimodal Digital Asset Management with CLIP & Sentence-Transformers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React/Vite development & production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(index_router)
app.include_router(search_router)
app.include_router(preview_router)

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "system": "AssetVault AI Digital Asset Management",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
