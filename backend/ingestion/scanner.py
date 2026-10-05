import os
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from backend.config import settings
from backend.models import Asset
from backend.ingestion.hasher import compute_md5

def get_file_type(extension: str) -> str:
    ext = extension.lower()
    if ext in settings.IMAGE_EXTENSIONS:
        return "image"
    if ext in settings.VIDEO_EXTENSIONS:
        return "video"
    if ext in settings.PDF_EXTENSIONS:
        return "pdf"
    return "unknown"

def scan_dataset(db: Session) -> dict:
    dataset_root = Path(settings.DATASET_PATH)
    if not dataset_root.exists():
        dataset_root.mkdir(parents=True, exist_ok=True)
        
    found_files = []
    seen_hashes = set()
    duplicates_skipped = 0
    unsupported_skipped = 0
    
    for root, _, files in os.walk(str(dataset_root)):
        for file in files:
            full_path = os.path.abspath(os.path.join(root, file))
            ext = os.path.splitext(file)[1].lower()
            
            file_type = get_file_type(ext)
            if file_type == "unknown":
                unsupported_skipped += 1
                continue
                
            try:
                md5_val = compute_md5(full_path)
            except Exception:
                continue
                
            if md5_val in seen_hashes:
                duplicates_skipped += 1
                continue
            seen_hashes.add(md5_val)
            
            size_bytes = os.path.getsize(full_path)
            existing = db.query(Asset).filter(Asset.md5_hash == md5_val).first()
            
            if existing:
                if existing.status in ("indexed", "partially_indexed"):
                    continue
                else: # failed, processing, or pending
                    existing.status = "pending"
                    existing.error_message = None
                    existing.filepath = full_path
                    existing.filename = file
                    existing.size_bytes = size_bytes
                    db.commit()
                    found_files.append(existing)
            else:
                new_asset = Asset(
                    id=str(uuid.uuid4()),
                    filename=file,
                    filepath=full_path,
                    file_type=file_type,
                    extension=ext,
                    size_bytes=size_bytes,
                    md5_hash=md5_val,
                    status="pending"
                )
                db.add(new_asset)
                db.commit()
                db.refresh(new_asset)
                found_files.append(new_asset)
                
    return {
        "pending_assets": found_files,
        "duplicates_skipped": duplicates_skipped,
        "unsupported_skipped": unsupported_skipped
    }
