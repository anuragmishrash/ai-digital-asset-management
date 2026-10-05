import os
import pdfplumber
from PIL import Image, ImageDraw
from backend.config import settings
from backend.ai_models import get_st_text_embedding
from backend.chroma_client import safe_upsert

def create_pdf_fallback_thumbnail(thumb_path: str, filename: str, page_count: int):
    img = Image.new("RGB", (400, 500), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 360, 460], fill=(248, 250, 252), outline=(148, 163, 184), width=2)
    draw.rectangle([40, 40, 360, 90], fill=(239, 68, 68))
    for y in range(120, 420, 25):
        draw.line([70, y, 330, y], fill=(203, 213, 225), width=4)
    img.save(thumb_path, "JPEG", quality=85)

def render_pdf_first_page_thumbnail(filepath: str, thumb_path: str, page_count: int, filename: str):
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(filepath)
        try:
            if len(pdf) > 0:
                page = pdf[0]
                image = page.render(scale=1.5).to_pil()
                image.thumbnail((400, 500), Image.Resampling.LANCZOS)
                image.save(thumb_path, "JPEG", quality=85)
                page.close()
                return
        finally:
            pdf.close()
    except Exception:
        pass
        
    create_pdf_fallback_thumbnail(thumb_path, filename, page_count)

def process_pdf(asset_id: str, filepath: str, filename: str) -> dict:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"PDF file does not exist: {filepath}")
        
    extracted_text = ""
    page_count = 0
    
    try:
        with pdfplumber.open(filepath) as pdf:
            page_count = len(pdf.pages)
            if page_count == 0:
                raise ValueError("Corrupted PDF: 0 pages found")
                
            page_texts = []
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    page_texts.append(text.strip())
            
            extracted_text = "\n\n".join(page_texts).strip()
            
    except Exception as e:
        raise ValueError(f"Corrupted or unreadable PDF document: {str(e)}")
        
    thumb_path = os.path.join(settings.THUMBNAILS_DIR, f"{asset_id}.jpg")
    render_pdf_first_page_thumbnail(filepath, thumb_path, page_count, filename)
    
    chroma_id = f"pdf_{asset_id}"
    if not extracted_text:
        note = f"Partially indexed: No extractable text found in PDF (scanned or image-only document). [Pages: {page_count}]"
        fallback_embedding = get_st_text_embedding(f"PDF Document: {filename}")
        safe_upsert(
            collection_name="pdf_collection",
            ids=[chroma_id],
            embeddings=[fallback_embedding],
            metadatas=[{
                "asset_id": asset_id,
                "filename": filename,
                "file_type": "pdf",
                "filepath": filepath,
                "pages": page_count,
                "description": note
            }],
            documents=[note]
        )
        return {
            "status": "partially_indexed",
            "ai_description": note,
            "chroma_id": chroma_id,
            "error_message": "No extractable text found (scanned PDF)"
        }
        
    clean_snippet = " ".join(extracted_text.split()[:80])
    ai_desc_full = f"PDF Document ({page_count} pages): {clean_snippet}..."
    embedding = get_st_text_embedding(extracted_text[:4000])
    
    safe_upsert(
        collection_name="pdf_collection",
        ids=[chroma_id],
        embeddings=[embedding],
        metadatas=[{
            "asset_id": asset_id,
            "filename": filename,
            "file_type": "pdf",
            "filepath": filepath,
            "pages": page_count,
            "description": ai_desc_full
        }],
        documents=[extracted_text[:2000]]
    )
    
    return {
        "status": "indexed",
        "ai_description": ai_desc_full,
        "chroma_id": chroma_id,
        "error_message": None
    }
