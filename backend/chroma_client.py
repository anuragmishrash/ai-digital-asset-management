import os
import threading
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.config import settings

_client = None
_client_lock = threading.RLock()

def get_chroma_client():
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = chromadb.PersistentClient(
                    path=settings.CHROMA_DB_PATH,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
    return _client

def get_image_collection():
    with _client_lock:
        client = get_chroma_client()
        return client.get_or_create_collection(
            name="image_video_collection",
            metadata={"hnsw:space": "cosine"}
        )

def get_pdf_collection():
    with _client_lock:
        client = get_chroma_client()
        return client.get_or_create_collection(
            name="pdf_collection",
            metadata={"hnsw:space": "cosine"}
        )

def safe_upsert(collection_name: str, ids: list, embeddings: list, metadatas: list, documents: list):
    with _client_lock:
        if collection_name == "image_video_collection":
            col = get_image_collection()
        else:
            col = get_pdf_collection()
        col.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

def safe_query(collection_name: str, query_embeddings: list, n_results: int, where: dict = None, include: list = None):
    with _client_lock:
        if collection_name == "image_video_collection":
            col = get_image_collection()
        else:
            col = get_pdf_collection()
        kwargs = {
            "query_embeddings": query_embeddings,
            "n_results": n_results
        }
        if where:
            kwargs["where"] = where
        if include:
            kwargs["include"] = include
        return col.query(**kwargs)

def reset_collections():
    global _client
    with _client_lock:
        client = get_chroma_client()
        try:
            client.delete_collection("image_video_collection")
        except Exception:
            pass
        try:
            client.delete_collection("pdf_collection")
        except Exception:
            pass
        client.get_or_create_collection(name="image_video_collection", metadata={"hnsw:space": "cosine"})
        client.get_or_create_collection(name="pdf_collection", metadata={"hnsw:space": "cosine"})
