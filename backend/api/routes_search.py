from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Asset
from backend.search.searcher import search_assets

router = APIRouter(prefix="/api", tags=["Search"])

@router.get("/search")
def search_endpoint(
    q: Optional[str] = Query(default="", description="Natural language search query"),
    type: Optional[str] = Query(default="all", description="File type filter: all, image, video, pdf"),
    limit: int = Query(default=30, ge=1, le=100),
    sort: str = Query(default="relevance", description="Sort by: relevance, date, file_size"),
    db: Session = Depends(get_db)
):
    """
    Perform natural language AI search over images, videos, and PDFs.
    """
    if not q or not q.strip():
        # Return all assets with optional filtering
        query = db.query(Asset)
        if type and type.lower() in ("image", "video", "pdf"):
            query = query.filter(Asset.file_type == type.lower())
            
        if sort == "date":
            query = query.order_by(Asset.created_at.desc())
        elif sort == "file_size":
            query = query.order_by(Asset.size_bytes.desc())
        else:
            query = query.order_by(Asset.updated_at.desc())
            
        assets = query.limit(limit).all()
        return {
            "query": "",
            "count": len(assets),
            "results": [
                {
                    **a.to_dict(),
                    "score": 1.0,
                    "similarity_percentage": 100,
                    "thumbnail_url": f"/api/thumbnail/{a.id}",
                    "file_url": f"/api/file/{a.id}"
                }
                for a in assets
            ]
        }
        
    results = search_assets(
        db=db,
        query=q.strip(),
        file_type=type,
        limit=limit,
        sort_by=sort
    )
    
    return {
        "query": q,
        "count": len(results),
        "results": results
    }

@router.get("/assets")
def list_assets(
    type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """List assets with metadata and pagination."""
    query = db.query(Asset)
    if type:
        query = query.filter(Asset.file_type == type.lower())
    if status:
        query = query.filter(Asset.status == status.lower())
        
    assets = query.order_by(Asset.created_at.desc()).limit(limit).all()
    return [
        {
            **a.to_dict(),
            "thumbnail_url": f"/api/thumbnail/{a.id}",
            "file_url": f"/api/file/{a.id}"
        }
        for a in assets
    ]
