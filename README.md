# AssetVault — AI-Powered Digital Asset Management

A full-stack AI-powered Digital Asset Management system that indexes images, videos, and PDF files and enables natural language semantic search across all of them.

## What It Does
- Scans a local folder of images, videos, and PDFs
- Uses AI (CLIP + Sentence Transformers) to understand file content
- Enables natural language search like "a woman standing with a cat" or "residential project brochure"
- Returns results ranked by semantic relevance
- Provides inline preview for all file types

## Tech Stack
- **Backend:** Python + FastAPI
- **Frontend:** React + Vite + Tailwind CSS
- **AI Models:** CLIP (openai/clip-vit-base-patch32) + Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store:** ChromaDB (local, persistent)
- **Database:** SQLite + SQLAlchemy
- **PDF Extraction:** pdfplumber
- **Video Processing:** OpenCV (keyframe extraction)

## Architecture
```
dataset/ (images + videos + pdfs)
↓
Scanner → MD5 hash check → skip if already indexed
↓
AI Processing:
Images → CLIP vision encoder → 512-dim embedding
Videos → OpenCV keyframes → CLIP on 5 frames → averaged embedding
PDFs → pdfplumber text → Sentence Transformer → 384-dim embedding
↓
ChromaDB (2 collections: image_video_assets, pdf_assets)
SQLite (metadata, status, descriptions)
↓
FastAPI search endpoint → embed query → vector similarity → ranked results
↓
React frontend → search bar → results grid → preview modal
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/anuragmishrash/ai-digital-asset-management.git
cd ai-digital-asset-management
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 3. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Install frontend dependencies
```bash
cd frontend
npm install
```

### 5. Prepare dataset
Create the dataset folder structure:
```bash
mkdir -p dataset/images dataset/videos dataset/pdfs
```
Place your images in `dataset/images/`, videos in `dataset/videos/`, PDFs in `dataset/pdfs/`

Or use the download scripts:
```bash
# Download images from Unsplash dataset
python scripts/download_images.py

# Download videos from Pixabay
python scripts/download_videos.py
```

### 6. Start the backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 7. Start the frontend
```bash
cd frontend
npm run dev
```

### 8. Open the app
Navigate to `http://localhost:5173`, click **Start Indexing**, wait for completion, then search.

## Dataset Summary
- **Images:** 520 (downloaded from Unsplash Lite Research Dataset)
- **Videos:** 82 (downloaded from Pixabay across 8 categories)
- **PDFs:** 25 (real estate and business brochures)
- **Total:** 627 files

## Search Evaluation

| # | Query | Expected | Relevant Results | Quality |
|---|-------|----------|-----------------|---------|
| 1 | a woman standing with a cat | Images of women with cats | ✅ Good |
| 2 | modern living room interior | Interior design images | ✅ Good |
| 3 | construction site activity | Construction videos | ✅ Good |
| 4 | residential project brochure | Real estate PDFs | ✅ Good |
| 5 | nature landscape with mountains | Nature images/videos | ✅ Good |
| 6 | people walking on street | Street scene images | ✅ Good |
| 7 | cooking in a kitchen | Kitchen videos | ✅ Good |
| 8 | animals in the wild | Wildlife images/videos | ✅ Good |
| 9 | gym workout exercise | Fitness videos | ✅ Good |
| 10 | financial quarterly report | Business PDFs | ✅ Good |

## Known Limitations
- Video processing is limited to keyframe sampling (5 frames), not full audio/speech analysis
- Scanned PDFs with no text layer are partially indexed
- First run requires internet to download AI models (~700 MB total, cached after)
- Large datasets (10GB+) will take significant time to index

## Production Improvements
- Add speech-to-text (Whisper) for video audio understanding
- OCR for scanned PDFs
- GPU acceleration for faster CLIP processing
- Cloud storage integration (S3, GCS)
- User authentication and multi-tenant support
- Distributed indexing for very large collections
