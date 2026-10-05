import os
import threading
import torch
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
from backend.config import settings

_clip_model = None
_clip_processor = None
_st_model = None
_candidate_label_features = None
_lock = threading.RLock()
_device = "cuda" if torch.cuda.is_available() else "cpu"

CANDIDATE_LABELS = [
    "a photograph of a person or people",
    "a woman standing with a cat",
    "a man working on a laptop in an office",
    "residential building architecture and luxury exterior",
    "modern interior design and living room furniture",
    "scenic nature landscape with mountains and lake",
    "sunset over the ocean beach",
    "city skyline with skyscrapers and traffic",
    "delicious food and cuisine on a dining table",
    "construction site with heavy machinery and workers",
    "business document brochure with charts and graphs",
    "modern technology electronic devices and gadgets",
    "happy domestic pets dogs and cats playing",
    "car or vehicle on a highway road",
    "abstract art painting with vibrant colors",
    "outdoor park with green trees and flowers",
    "aerial drone shot of real estate property",
    "wildlife animal in natural habitat",
    "sports fitness workout and athletic training",
    "medical healthcare setting with doctors or equipment"
]

def get_device():
    global _device
    return _device

def get_clip():
    global _clip_model, _clip_processor, _candidate_label_features
    if _clip_model is None or _clip_processor is None:
        with _lock:
            if _clip_model is None or _clip_processor is None:
                model_name = settings.CLIP_MODEL_NAME
                processor = CLIPProcessor.from_pretrained(model_name)
                model = CLIPModel.from_pretrained(model_name)
                model.to(get_device())
                model.eval()
                _clip_processor = processor
                _clip_model = model
                
                inputs = processor(text=CANDIDATE_LABELS, return_tensors="pt", padding=True, truncation=True).to(get_device())
                with torch.no_grad():
                    feats = model.get_text_features(**inputs)
                    feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
                    _candidate_label_features = feats
                    
    return _clip_model, _clip_processor

def get_sentence_transformer():
    global _st_model
    if _st_model is None:
        with _lock:
            if _st_model is None:
                _st_model = SentenceTransformer(settings.ST_MODEL_NAME, device=get_device())
    return _st_model

def get_image_embedding(pil_image: Image.Image) -> list:
    model, processor = get_clip()
    inputs = processor(images=pil_image, return_tensors="pt").to(get_device())
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
    return image_features.cpu().squeeze(0).tolist()

def get_batch_image_embeddings(pil_images: list) -> list:
    if not pil_images:
        return []
    model, processor = get_clip()
    inputs = processor(images=pil_images, return_tensors="pt").to(get_device())
    with torch.no_grad():
        features = model.get_image_features(**inputs)
        features = features / features.norm(p=2, dim=-1, keepdim=True)
    return features.cpu().numpy()

def get_clip_text_embedding(text: str) -> list:
    model, processor = get_clip()
    inputs = processor(text=[text], return_tensors="pt", padding=True, truncation=True).to(get_device())
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
    return text_features.cpu().squeeze(0).tolist()

def get_st_text_embedding(text: str) -> list:
    model = get_sentence_transformer()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def generate_image_description(pil_image: Image.Image, image_features: list = None) -> str:
    try:
        model, processor = get_clip()
        if image_features is not None:
            img_tensor = torch.tensor(image_features, device=get_device()).unsqueeze(0)
        else:
            inputs = processor(images=pil_image, return_tensors="pt").to(get_device())
            with torch.no_grad():
                img_tensor = model.get_image_features(**inputs)
                img_tensor = img_tensor / img_tensor.norm(p=2, dim=-1, keepdim=True)
                
        with torch.no_grad():
            similarity = (img_tensor @ _candidate_label_features.T).squeeze(0)
            probs = torch.softmax(similarity * 100.0, dim=0).cpu().numpy()
            
        top_indices = np.argsort(probs)[::-1][:3]
        top_matches = [CANDIDATE_LABELS[i] for i in top_indices if probs[i] > 0.05]
        
        if top_matches:
            primary = top_matches[0].capitalize()
            if len(top_matches) > 1:
                secondary = top_matches[1]
                return f"AI Visual Analysis: {primary}; related to {secondary}."
            return f"AI Visual Analysis: {primary}."
        return f"AI Visual Analysis: Visual scene matching '{CANDIDATE_LABELS[top_indices[0]]}'."
    except Exception as e:
        return f"AI Visual Analysis: Image asset with resolution {pil_image.size[0]}x{pil_image.size[1]} ({e})"
