import os
import cv2
import numpy as np
from PIL import Image
from backend.config import settings
from backend.ai_models import get_batch_image_embeddings, generate_image_description
from backend.chroma_client import safe_upsert

def process_video(asset_id: str, filepath: str, filename: str) -> dict:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Video file does not exist: {filepath}")
        
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise ValueError("Corrupted or unsupported video stream: unable to open with OpenCV")
        
    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if total_frames <= 0 or fps <= 0:
            raise ValueError("Corrupted video file: 0 frames or invalid FPS detected")
            
        duration_sec = round(total_frames / fps, 2)
        sample_percentages = [0.10, 0.25, 0.50, 0.75, 0.90]
        frame_indices = [min(int(p * total_frames), total_frames - 1) for p in sample_percentages]
        frame_indices = sorted(list(set(frame_indices)))
        
        keyframes = []
        for f_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
            ret, frame = cap.read()
            if ret and frame is not None:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_frame = Image.fromarray(rgb_frame)
                keyframes.append(pil_frame)
                
        if not keyframes:
            raise ValueError("Could not extract any valid keyframes from video")
            
        thumb_path = os.path.join(settings.THUMBNAILS_DIR, f"{asset_id}.jpg")
        thumb = keyframes[0].copy()
        thumb.thumbnail((400, 400), Image.Resampling.LANCZOS)
        thumb.save(thumb_path, "JPEG", quality=85)
        
        # Batch extract embeddings in one single forward pass
        keyframe_embeddings = get_batch_image_embeddings(keyframes)
        mean_embedding = np.mean(keyframe_embeddings, axis=0)
        norm = np.linalg.norm(mean_embedding)
        if norm > 0:
            mean_embedding = mean_embedding / norm
        final_embedding = mean_embedding.tolist()
        
        # Generate description from keyframe 0
        primary_desc = generate_image_description(keyframes[0], image_features=final_embedding)
        ai_desc_full = (
            f"AI Video Analysis: {primary_desc} "
            f"[Duration: {duration_sec}s, FPS: {round(fps, 1)}, Frames: {total_frames}, Resolution: {width}x{height}]"
        )
        
    finally:
        cap.release()
        
    chroma_id = f"vid_{asset_id}"
    safe_upsert(
        collection_name="image_video_collection",
        ids=[chroma_id],
        embeddings=[final_embedding],
        metadatas=[{
            "asset_id": asset_id,
            "filename": filename,
            "file_type": "video",
            "filepath": filepath,
            "duration": duration_sec,
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
