import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "AssetVault - AI DAM"
    DATASET_PATH: str = str(BASE_DIR / "dataset")
    DATA_DIR: str = str(BASE_DIR / "data")
    SQLITE_DB_PATH: str = str(BASE_DIR / "data" / "assets.db")
    CHROMA_DB_PATH: str = str(BASE_DIR / "data" / "chromadb")
    THUMBNAILS_DIR: str = str(BASE_DIR / "data" / "thumbnails")
    
    # AI Models
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch32"
    ST_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Ingestion configuration
    MAX_VIDEO_KEYFRAMES: int = 5
    INDEXING_BATCH_SIZE: int = 10
    MAX_WORKERS: int = 4
    
    # Supported file extensions
    IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
    VIDEO_EXTENSIONS: set = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    PDF_EXTENSIONS: set = {".pdf"}
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
Path(settings.DATASET_PATH).mkdir(parents=True, exist_ok=True)
Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)
Path(settings.THUMBNAILS_DIR).mkdir(parents=True, exist_ok=True)

(Path(settings.DATASET_PATH) / "images").mkdir(parents=True, exist_ok=True)
(Path(settings.DATASET_PATH) / "videos").mkdir(parents=True, exist_ok=True)
(Path(settings.DATASET_PATH) / "pdfs").mkdir(parents=True, exist_ok=True)
