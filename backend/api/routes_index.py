import os
import shutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Asset
from backend.config import settings
from backend.chroma_client import reset_collections
from backend.ingestion.indexer import indexing_manager, trigger_indexing

router = APIRouter(prefix="/api", tags=["Indexing"])

@router.post("/index/start")
async def start_indexing():
    """Trigger dataset scan and background AI indexing."""
    result = await trigger_indexing()
    return result

@router.get("/index/status")
def get_indexing_status(db: Session = Depends(get_db)):
    """Return pollable real-time status and logs."""
    return indexing_manager.get_status(db)

@router.delete("/index/reset")
def reset_all_data(db: Session = Depends(get_db)):
    """Wipes SQLite assets and ChromaDB collections for a fresh reindex."""
    if indexing_manager.is_running:
        raise HTTPException(status_code=400, detail="Cannot reset while indexing is actively running")
        
    # Clear SQLite table
    db.query(Asset).delete()
    db.commit()
    
    # Reset ChromaDB collections
    reset_collections()
    
    # Clear thumbnail cache
    thumb_dir = settings.THUMBNAILS_DIR
    if os.path.exists(thumb_dir):
        for f in os.listdir(thumb_dir):
            file_path = os.path.join(thumb_dir, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception:
                pass
                
    indexing_manager.logs.clear()
    indexing_manager.add_log("info", "Database and vector store reset successfully.")
    
    return {"status": "success", "message": "All assets, vectors, and thumbnails cleared."}

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """Get system-wide summary analytics."""
    total_assets = db.query(Asset).count()
    images_count = db.query(Asset).filter(Asset.file_type == "image").count()
    videos_count = db.query(Asset).filter(Asset.file_type == "video").count()
    pdfs_count = db.query(Asset).filter(Asset.file_type == "pdf").count()
    total_bytes = db.query(func.sum(Asset.size_bytes)).scalar() or 0
    
    return {
        "total_assets": total_assets,
        "images": images_count,
        "videos": videos_count,
        "pdfs": pdfs_count,
        "total_bytes": total_bytes,
        "is_indexing": indexing_manager.is_running
    }
