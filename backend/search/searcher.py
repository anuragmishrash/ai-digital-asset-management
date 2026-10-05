from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from backend.models import Asset
from backend.chroma_client import safe_query, get_image_collection, get_pdf_collection
from backend.ai_models import get_clip_text_embedding, get_st_text_embedding

def search_assets(
    db: Session,
    query: str,
    file_type: Optional[str] = None,
    limit: int = 20,
    sort_by: str = "relevance"
) -> List[Dict]:
    """
    Unified multimodal natural language search:
    1. Embed query with CLIP for images & videos (if file_type != 'pdf')
    2. Embed query with SentenceTransformer for PDFs (if file_type != 'image' and != 'video')
    3. Query respective ChromaDB collections
    4. Merge, normalize scores, deduplicate
    5. Enrich with SQLite metadata and sort
    """
    raw_hits = {}
    normalized_type = file_type.lower() if file_type else "all"
    
    # 1. Search Image/Video Collection via CLIP
    if normalized_type in ("all", "image", "video", ""):
        try:
            clip_embedding = get_clip_text_embedding(query)
            image_col = get_image_collection()
            count = image_col.count()
            
            if count > 0:
                where_filter = None
                if normalized_type in ("image", "video"):
                    where_filter = {"file_type": normalized_type}
                    
                img_results = safe_query(
                    collection_name="image_video_collection",
                    query_embeddings=[clip_embedding],
                    n_results=min(limit * 2, count),
                    where=where_filter,
                    include=["metadatas", "distances", "documents"]
                )
                
                if img_results and "ids" in img_results and len(img_results["ids"]) > 0:
                    ids = img_results["ids"][0]
                    distances = img_results.get("distances", [[]])[0]
                    metadatas = img_results.get("metadatas", [[]])[0]
                    
                    for i, cid in enumerate(ids):
                        meta = metadatas[i] if i < len(metadatas) else {}
                        asset_id = meta.get("asset_id") or cid.replace("img_", "").replace("vid_", "")
                        dist = distances[i] if i < len(distances) else 1.0
                        
                        # Cosine similarity for CLIP (dist = 1 - cos_sim)
                        cos_sim = 1.0 - dist
                        # Calibrate score: typical CLIP positive match is cos_sim >= 0.18 to 0.35
                        calibrated = max(0.0, min(1.0, (cos_sim - 0.10) / 0.22)) if cos_sim > 0.10 else max(0.05, cos_sim)
                        
                        raw_hits[asset_id] = {
                            "score": round(calibrated, 4),
                            "raw_sim": cos_sim,
                            "distance": dist,
                            "metadata": meta
                        }
        except Exception as e:
            print(f"Error querying image/video collection: {e}")

    # 2. Search PDF Collection via SentenceTransformer
    if normalized_type in ("all", "pdf", ""):
        try:
            st_embedding = get_st_text_embedding(query)
            pdf_col = get_pdf_collection()
            count = pdf_col.count()
            
            if count > 0:
                pdf_results = safe_query(
                    collection_name="pdf_collection",
                    query_embeddings=[st_embedding],
                    n_results=min(limit * 2, count),
                    include=["metadatas", "distances", "documents"]
                )
                
                if pdf_results and "ids" in pdf_results and len(pdf_results["ids"]) > 0:
                    ids = pdf_results["ids"][0]
                    distances = pdf_results.get("distances", [[]])[0]
                    metadatas = pdf_results.get("metadatas", [[]])[0]
                    
                    for i, cid in enumerate(ids):
                        meta = metadatas[i] if i < len(metadatas) else {}
                        asset_id = meta.get("asset_id") or cid.replace("pdf_", "")
                        dist = distances[i] if i < len(distances) else 1.0
                        
                        # Cosine similarity for SentenceTransformer
                        cos_sim = 1.0 - dist
                        calibrated = max(0.0, min(1.0, (cos_sim - 0.15) / 0.55)) if cos_sim > 0.15 else max(0.05, cos_sim)
                        
                        if asset_id in raw_hits:
                            if calibrated > raw_hits[asset_id]["score"]:
                                raw_hits[asset_id] = {
                                    "score": round(calibrated, 4),
                                    "raw_sim": cos_sim,
                                    "distance": dist,
                                    "metadata": meta
                                }
                        else:
                            raw_hits[asset_id] = {
                                "score": round(calibrated, 4),
                                "raw_sim": cos_sim,
                                "distance": dist,
                                "metadata": meta
                            }
        except Exception as e:
            print(f"Error querying PDF collection: {e}")

    # 3. Retrieve DB records
    if not raw_hits:
        keyword_query = db.query(Asset)
        if normalized_type in ("image", "video", "pdf"):
            keyword_query = keyword_query.filter(Asset.file_type == normalized_type)
        if query and query.strip():
            search_pattern = f"%{query.strip()}%"
            keyword_query = keyword_query.filter(
                (Asset.filename.ilike(search_pattern)) | 
                (Asset.ai_description.ilike(search_pattern))
            )
        db_assets = keyword_query.limit(limit).all()
        results = []
        for asset in db_assets:
            results.append({
                **asset.to_dict(),
                "score": 0.5,
                "similarity_percentage": 50,
                "thumbnail_url": f"/api/thumbnail/{asset.id}",
                "file_url": f"/api/file/{asset.id}"
            })
        return results

    hit_ids = list(raw_hits.keys())
    db_assets = db.query(Asset).filter(Asset.id.in_(hit_ids)).all()
    asset_map = {a.id: a for a in db_assets}
    
    results = []
    for asset_id, hit_data in raw_hits.items():
        asset = asset_map.get(asset_id)
        if not asset:
            continue
            
        score = hit_data["score"]
        percentage = min(99, max(5, int(score * 100)))
        
        results.append({
            **asset.to_dict(),
            "score": score,
            "similarity_percentage": percentage,
            "thumbnail_url": f"/api/thumbnail/{asset.id}",
            "file_url": f"/api/file/{asset.id}"
        })
        
    # 4. Sorting
    if sort_by == "date":
        results.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    elif sort_by == "file_size":
        results.sort(key=lambda x: x.get("size_bytes") or 0, reverse=True)
    else: # relevance
        results.sort(key=lambda x: x["score"], reverse=True)
        
    return results[:limit]
