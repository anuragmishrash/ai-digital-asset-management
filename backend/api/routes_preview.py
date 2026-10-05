import os
import mimetypes
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Asset
from backend.config import settings

router = APIRouter(prefix="/api", tags=["Preview"])

@router.get("/preview/{asset_id}")
def get_asset_preview(asset_id: str, db: Session = Depends(get_db)):
    """Return detailed metadata and AI analysis for an asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    file_exists = os.path.exists(asset.filepath)
    
    return {
        **asset.to_dict(),
        "file_exists": file_exists,
        "thumbnail_url": f"/api/thumbnail/{asset.id}",
        "file_url": f"/api/file/{asset.id}"
    }

@router.get("/file/{asset_id}")
def serve_asset_file(asset_id: str, db: Session = Depends(get_db)):
    """Serve the raw media file with proper MIME headers."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    if not os.path.exists(asset.filepath):
        raise HTTPException(status_code=404, detail="Original file missing from filesystem")
        
    mime_type, _ = mimetypes.guess_type(asset.filepath)
    if not mime_type:
        if asset.file_type == "image":
            mime_type = "image/jpeg"
        elif asset.file_type == "video":
            mime_type = "video/mp4"
        elif asset.file_type == "pdf":
            mime_type = "application/pdf"
        else:
            mime_type = "application/octet-stream"
            
    return FileResponse(
        path=asset.filepath,
        media_type=mime_type,
        filename=asset.filename
    )

@router.get("/thumbnail/{asset_id}")
def serve_thumbnail(asset_id: str, db: Session = Depends(get_db)):
    """Serve high-performance pre-rendered thumbnail."""
    thumb_path = os.path.join(settings.THUMBNAILS_DIR, f"{asset_id}.jpg")
    
    if os.path.exists(thumb_path):
        return FileResponse(thumb_path, media_type="image/jpeg")
        
    # Fallback to serving original file if it's an image
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset and os.path.exists(asset.filepath) and asset.file_type == "image":
        mime_type, _ = mimetypes.guess_type(asset.filepath)
        return FileResponse(asset.filepath, media_type=mime_type or "image/jpeg")
        
    # Return 404 if no thumbnail exists yet
    raise HTTPException(status_code=404, detail="Thumbnail not ready")
