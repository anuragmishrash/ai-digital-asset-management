from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True)        # UUID
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    file_type = Column(String)                   # image / video / pdf
    extension = Column(String)
    size_bytes = Column(Integer)
    md5_hash = Column(String, unique=True, index=True)       # for dedup
    status = Column(String, default="pending")   # pending/processing/indexed/partially_indexed/failed
    error_message = Column(String, nullable=True)
    ai_description = Column(Text, nullable=True)
    chroma_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "filepath": self.filepath,
            "file_type": self.file_type,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "md5_hash": self.md5_hash,
            "status": self.status,
            "error_message": self.error_message,
            "ai_description": self.ai_description,
            "chroma_id": self.chroma_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
