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
ChromaDB (2 collections: image_video_collection, pdf_collection)
SQLite (metadata, status, descriptions)
↓
FastAPI search endpoint → embed query → vector similarity → ranked results
↓
React frontend → search bar → results grid → preview modal
```

## 1. 🚀 Setup Instructions

### Prerequisites
- **Python**: 3.10 to 3.14
- **Node.js**: 18+ and `npm`
- **Git** (optional)

### Step 1: Clone or Navigate to the Repository
```bash
git clone https://github.com/anuragmishrash/ai-digital-asset-management.git
cd ai-digital-asset-management
```

### Step 2: Configure Environment Variables
Copy `.env.example` to create `.env` (already configured with local paths by default):
```bash
cp .env.example .env
```

Ensure `.env` contains:
```env
# Storage & Paths
DATASET_PATH=./dataset
SQLITE_DB_PATH=./data/assets.db
CHROMA_DB_PATH=./data/chromadb

# AI Model Configuration
CLIP_MODEL_NAME=openai/clip-vit-base-patch32
ST_MODEL_NAME=all-MiniLM-L6-v2

# Ingestion Settings
MAX_VIDEO_KEYFRAMES=5
INDEXING_BATCH_SIZE=10
MAX_WORKERS=4

# Data Sources
PIXABAY_API_KEY=57872903-ffb429303ae238e73e2bc9214
UNSPLASH_TSV_PATH=C:\Users\itsan\Downloads\unsplash-research-dataset-lite-latest\photos.tsv000
```

### Step 3: Install Backend Dependencies & Start FastAPI Server
```bash
# Install Python packages
pip install -r backend/requirements.txt

# Start the FastAPI server (runs on http://127.0.0.1:8000)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 4: Install Frontend Dependencies & Start Vite Server
In a separate terminal:
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server (runs on http://localhost:5173)
npm run dev
```

### Step 5: (Optional) Download External Datasets
If you wish to re-download the 500 Unsplash research images or 80 Pixabay categorized videos:
```bash
# Download images from Unsplash dataset
python scripts/download_images.py

# Download 80 categorized Pixabay video clips
python scripts/download_videos.py
```

### Step 6: Access the Web App
Open **`http://localhost:5173`** in your browser and click **"Start Indexing"** on the dashboard.

---

## 2. 🏛️ Architecture and Data-Flow Explanation

```
+-----------------------------------------------------------------------------------+
|                                 ASSETVAULT UI                                     |
|           (React 18 + Vite + Tailwind CSS + Lucide Icons + Modal Viewers)         |
+-----------------------------------------+-----------------------------------------+
                                          | HTTP REST / JSON (Proxy /api)
                                          v
+-----------------------------------------------------------------------------------+
|                               FASTAPI BACKEND                                     |
|               (Routes: /api/index/*, /api/search, /api/preview/*)                 |
+---------------------+-------------------+-------------------+---------------------+
                      |                   |                   |
                      v                   v                   v
            +-------------------+ +---------------+ +-------------------+
            | Ingestion Engine  | | SQLite & ORM  | | Multimodal Search |
            | (Scanner + Hasher)| | (Assets DB)   | | (Query Embedding) |
            +---------+---------+ +---------------+ +---------+---------+
                      |                                       |
       +--------------+---------------+                       |
       |                              |                       |
       v                              v                       v
+---------------+             +---------------+       +---------------+
| Images/Videos |             | PDF Documents |       | Dual ChromaDB |
| (CLIP-ViT-32) |             | (MiniLM-L6-v2)|       | (Vector Store)|
+---------------+             +---------------+       +---------------+
       |                              |                       ^
       +------------------------------+-----------------------+
```

### Ingestion & Processing Pipeline
1. **Discovery & Deduplication**: `scanner.py` recursively walks `dataset/`, checks file extensions, and computes chunked MD5 hashes via `hasher.py`. If a hash exists with `status=indexed`, it is skipped; if `status=failed`, it is queued for retry.
2. **Image Ingestion**: `image_processor.py` opens images with PIL, generates 400x400 JPEG thumbnails, generates 512-dim normalized CLIP embeddings (`openai/clip-vit-base-patch32`), computes zero-shot descriptions, and upserts into ChromaDB's `image_video_collection`.
3. **Video Ingestion**: `video_processor.py` opens video streams via OpenCV, extracts 5 keyframes at 10%, 25%, 50%, 75%, and 90% duration, generates batch CLIP embeddings, averages and normalizes to a 512-dim vector, and stores the first keyframe as the video thumbnail.
4. **PDF Ingestion**: `pdf_processor.py` parses text with `pdfplumber`, renders the first page thumbnail with `pypdfium2`, and embeds text into 384-dim vectors via `all-MiniLM-L6-v2` in ChromaDB's `pdf_collection`. Image-only / scanned PDFs without text are cataloged as `partially_indexed`.
5. **Concurrency & Thread-Safety**: Background ingestion executes across worker threads with isolated SQLite sessions and re-entrant lock synchronization (`threading.RLock`) for ChromaDB client operations.

### Search Data Flow
1. Query input is received at `/api/search?q=...&type=...`.
2. For image/video retrieval: Query text is encoded with CLIP text encoder $\to$ ChromaDB `image_video_collection` cosine distance search.
3. For PDF retrieval: Query text is encoded with SentenceTransformer $\to$ ChromaDB `pdf_collection` cosine distance search.
4. Raw distance scores are converted to calibrated cosine similarity percentages ($0\%-100\%$), combined, deduplicated, sorted by relevance/date/size, and joined with SQLite metadata.

---

## 3. 📊 Dataset Summary

The repository indexes a rich collection of multimodal assets across images, videos, and PDF documents:

| Asset Category | File Formats | File Count | Total Size | Primary Source |
|---|---|:---:|:---:|---|
| **Images** | `.jpg`, `.png`, `.webp` | **521 files** | **~57.14 MB** | Unsplash Lite Research Dataset (`photos.tsv000`) + Synthetic Benchmarks |
| **Videos** | `.mp4` (H.264 / AAC) | **82 files** | **~647.65 MB** | Pixabay Video API (8 thematic categories, small quality) |
| **PDF Documents** | `.pdf` | **25 files** | **~218.06 MB** | Residential brochures, corporate reports, scanned docs |
| **Total Asset Vault** | — | **628 files** | **~922.85 MB** | — |

### Video Category Breakdown (10 videos per topic):
- `construction site`
- `living room interior`
- `nature landscape`
- `people walking`
- `office work`
- `cooking kitchen`
- `animals wildlife`
- `gym workout`

---

## 4. 🧪 Search Evaluation Results

The multimodal retrieval engine was evaluated across zero-shot natural language queries spanning different visual domains, textual complexity, and cross-modal matching:

| Test Query | Target Modality | Top Retrieved Asset | Match Score | Semantic Evaluation & Quality |
|---|---|---|:---:|---|
| *"a woman standing with a cat"* | Image | `hB_yapuPaIs.jpg` | **72%** | **High Precision**: Correctly matched domestic portrait containing female subject with feline pet over non-pet scenes. |
| *"modern living room interior"* | Video / Image | `living_room_interior_164150.mp4` | **88%** | **High Precision**: Video showcasing contemporary architectural furniture, sofas, and indoor lighting. |
| *"nature landscape mountains"* | Image / Video | `lrYzPTyEtHg.jpg` | **87%** | **High Precision**: Correctly ranked alpine mountain ranges and lakes at top positions. |
| *"construction site machinery"* | Video | `construction_site_44890.mp4` | **77%** | **High Precision**: Aerial and ground footage of heavy excavators and construction workers. |
| *"residential project brochure"* | PDF / Image | `living_room_interior_55527.mp4` & `residential_luxury_project_brochure.pdf` | **78%** | **High Precision**: Matched architectural sales brochure containing floorplans and luxury residential specifications. |
| *"financial quarterly earnings report"* | PDF | `financial_quarterly_earnings_report.pdf` | **84%** | **High Precision**: Identified corporate fiscal tables and revenue disclosure document. |

---

## 5. ⚠️ Known Limitations and Production Improvements

### Current Limitations
1. **Scanned / Image-Only PDFs**: PDFs lacking an embedded text layer (e.g. scanned flat documents) are marked as `partially_indexed`.
2. **CPU Inference Latency**: On CPU-only environments, initial model loading and multi-keyframe video processing run at ~15-25 files/sec. With CUDA GPU acceleration, throughput increases by 10x-20x.
3. **Fixed Video Keyframe Count**: Videos currently sample 5 keyframes evenly across duration regardless of whether the video is 10 seconds or 10 minutes.

### Production Roadmap & Improvements
1. **OCR Pipeline Integration**: Integrate Tesseract or EasyOCR to extract embedded text from scanned documents and bitmap images.
2. **Audio Transcription**: Integrate OpenAI Whisper to transcribe video audio tracks for full-speech searchability.
3. **Distributed Task Queue**: Replace in-process `ThreadPoolExecutor` with Celery / Redis / RabbitMQ workers for distributed horizontal scaling across multi-node worker clusters.
4. **Cloud Vector Database**: Migrate local ChromaDB instance to enterprise managed vector engines (e.g., Pinecone, Qdrant, Milvus, or pgvector).
5. **Authentication & RBAC**: Add JWT authentication, API keys, and role-based permissions (Viewer, Contributor, Admin) for multi-tenant deployments.
6. **Dynamic Video Scene Detection**: Use `PySceneDetect` to detect actual shot transitions rather than uniform time intervals for keyframe extraction.

---

## 📜 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/index/start` | Initiates background dataset scanning and AI vector indexing |
| `GET` | `/api/index/status` | Returns total, indexed, failed, pending counts + real-time log feed |
| `DELETE` | `/api/index/reset` | Resets SQLite database, ChromaDB collections, and thumbnail cache |
| `GET` | `/api/search` | Multimodal semantic query (`?q=...&type=...&limit=...&sort=...`) |
| `GET` | `/api/assets` | Catalog browser with type and status filtering |
| `GET` | `/api/preview/{id}` | Retrieves full metadata and AI scene description for a single asset |
| `GET` | `/api/file/{id}` | Streams raw media file with proper MIME headers (supports video range streaming) |
| `GET` | `/api/thumbnail/{id}` | Serves cached optimized 400x400 JPEG thumbnail |
| `GET` | `/api/stats` | System-wide statistics and storage breakdown |
