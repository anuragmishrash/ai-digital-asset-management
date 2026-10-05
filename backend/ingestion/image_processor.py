import os
import csv
from pathlib import Path
from PIL import Image, ImageOps
from backend.config import settings
from backend.ai_models import get_image_embedding, generate_image_description
from backend.chroma_client import safe_upsert

_metadata_cache = None

def get_image_metadata_map():
    global _metadata_cache
    if _metadata_cache is None:
        _metadata_cache = {}
        meta_csv = Path(settings.DATASET_PATH) / "images" / "_metadata.csv"
        if meta_csv.exists():
            try:
                with open(meta_csv, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        pid = row.get("photo_id", "").strip()
                        if pid:
                            _metadata_cache[pid] = {
                                "photo_description": row.get("photo_description", "").strip(),
                                "ai_description": row.get("ai_description", "").strip()
                            }
            except Exception as e:
                print(f"Notice: Could not load _metadata.csv: {e}")
    return _metadata_cache

def process_image(asset_id: str, filepath: str, filename: str) -> dict:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Image file does not exist: {filepath}")
    
    try:
        with Image.open(filepath) as img:
            rgb_image = ImageOps.exif_transpose(img).convert("RGB")
            
            thumb_path = os.path.join(settings.THUMBNAILS_DIR, f"{asset_id}.jpg")
            thumb = rgb_image.copy()
            thumb.thumbnail((400, 400), Image.Resampling.LANCZOS)
            thumb.save(thumb_path, "JPEG", quality=85)
            
            width, height = rgb_image.size
            embedding = get_image_embedding(rgb_image)
            zero_shot_desc = generate_image_description(rgb_image)
            
            # Enrich with Unsplash metadata if available
            photo_base = os.path.splitext(filename)[0]
            meta_map = get_image_metadata_map()
            meta_entry = meta_map.get(photo_base, {})
            
            dataset_desc = meta_entry.get("photo_description") or meta_entry.get("ai_description") or ""
            
            if dataset_desc:
                ai_desc_full = f"{dataset_desc}. ({zero_shot_desc}) [Resolution: {width}x{height}]"
            else:
                ai_desc_full = f"{zero_shot_desc} [Resolution: {width}x{height}, Format: {img.format or 'JPEG'}]"
            
    except Exception as e:
        raise ValueError(f"Corrupted or unreadable image file: {str(e)}")
    
    chroma_id = f"img_{asset_id}"
    safe_upsert(
        collection_name="image_video_collection",
        ids=[chroma_id],
        embeddings=[embedding],
        metadatas=[{
            "asset_id": asset_id,
            "filename": filename,
            "file_type": "image",
            "filepath": filepath,
            "description": ai_desc_full
        }],
        documents=[ai_desc_full]
    )
    
    return {
        "status": "indexed",
        "ai_description": ai_desc_full,
        "chroma_id": chroma_id,
        "error_message": None
    }
