import asyncio
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from backend.config import settings
from backend.database import SessionLocal
from backend.models import Asset
from backend.ingestion.scanner import scan_dataset
from backend.ingestion.image_processor import process_image
from backend.ingestion.video_processor import process_video
from backend.ingestion.pdf_processor import process_pdf

class IndexingManager:
    def __init__(self):
        self.is_running = False
        self.current_file = ""
        self.start_time = None
        self.logs = []
        self.max_logs = 100
        self._lock = asyncio.Lock()
        
    def add_log(self, level: str, message: str, asset_id: str = None, filename: str = None):
        log_entry = {
            "time": datetime.utcnow().strftime("%H:%M:%S"),
            "level": level,  # info, success, warning, error
            "message": message,
            "asset_id": asset_id,
            "filename": filename
        }
        self.logs.insert(0, log_entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop()

    def get_status(self, db: Session) -> dict:
        total = db.query(Asset).count()
        indexed = db.query(Asset).filter(Asset.status == "indexed").count()
        partially_indexed = db.query(Asset).filter(Asset.status == "partially_indexed").count()
        failed = db.query(Asset).filter(Asset.status == "failed").count()
        pending = db.query(Asset).filter(Asset.status == "pending").count()
        processing = db.query(Asset).filter(Asset.status == "processing").count()
        
        # Recent asset statuses
        recent_assets = db.query(Asset).order_by(Asset.updated_at.desc()).limit(25).all()
        
        return {
            "is_running": self.is_running,
            "current_file": self.current_file,
            "counts": {
                "total": total,
                "indexed": indexed + partially_indexed,
                "fully_indexed": indexed,
                "partially_indexed": partially_indexed,
                "failed": failed,
                "pending": pending,
                "processing": processing
            },
            "recent_assets": [a.to_dict() for a in recent_assets],
            "logs": self.logs
        }

    def _process_single_asset(self, asset_id: str):
        """Process a single asset with an isolated database session."""
        db = SessionLocal()
        try:
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                return
                
            self.current_file = asset.filename
            asset.status = "processing"
            asset.updated_at = datetime.utcnow()
            db.commit()
            
            self.add_log("info", f"Processing {asset.file_type}: {asset.filename}", asset_id, asset.filename)
            
            filepath = asset.filepath
            filename = asset.filename
            file_type = asset.file_type
            
            result = None
            if file_type == "image":
                result = process_image(asset_id, filepath, filename)
            elif file_type == "video":
                result = process_video(asset_id, filepath, filename)
            elif file_type == "pdf":
                result = process_pdf(asset_id, filepath, filename)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
            # Update database record
            asset.status = result.get("status", "indexed")
            asset.ai_description = result.get("ai_description")
            asset.chroma_id = result.get("chroma_id")
            asset.error_message = result.get("error_message")
            asset.updated_at = datetime.utcnow()
            db.commit()
            
            status_level = "success" if asset.status == "indexed" else "warning"
            self.add_log(status_level, f"Successfully indexed {asset.filename}", asset_id, asset.filename)
            
        except Exception as e:
            error_msg = str(e)
            if asset:
                asset.status = "failed"
                asset.error_message = error_msg
                asset.updated_at = datetime.utcnow()
                db.commit()
            self.add_log("error", f"Failed {asset.filename if asset else asset_id}: {error_msg}", asset_id, asset.filename if asset else None)
        finally:
            db.close()

    def run_indexing_sync(self):
        """Synchronous runner executed inside a worker thread."""
        self.is_running = True
        self.start_time = time.time()
        self.add_log("info", "Starting dataset scanner...")
        
        db = SessionLocal()
        try:
            scan_res = scan_dataset(db)
            pending_assets = scan_res["pending_assets"]
            duplicates = scan_res["duplicates_skipped"]
            
            self.add_log("info", f"Scan complete: {len(pending_assets)} files queued for processing ({duplicates} duplicates skipped).")
            
            if not pending_assets:
                self.add_log("info", "All files in dataset are already up-to-date.")
                self.is_running = False
                self.current_file = ""
                return
                
            asset_ids = [a.id for a in pending_assets]
            
            # Process in thread pool
            with ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
                # Use map / list to execute batch
                list(executor.map(self._process_single_asset, asset_ids))
                
            self.add_log("success", "Indexing pipeline finished successfully!")
            
        except Exception as e:
            self.add_log("error", f"Critical indexing error: {str(e)}")
        finally:
            self.is_running = False
            self.current_file = ""
            db.close()

# Global singleton
indexing_manager = IndexingManager()

async def trigger_indexing():
    """Trigger background indexing task safely without blocking event loop."""
    if indexing_manager.is_running:
        return {"status": "already_running", "message": "Indexing is already in progress"}
        
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, indexing_manager.run_indexing_sync)
    return {"status": "started", "message": "Indexing started in background"}
