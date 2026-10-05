import os
import json
import urllib.parse
import urllib.request
import concurrent.futures
from pathlib import Path

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "57872903-ffb429303ae238e73e2bc9214")
BASE_URL = "https://pixabay.com/api/videos/"
OUTPUT_DIR = Path("dataset/videos")
VIDEOS_PER_TERM = 10
MAX_WORKERS = 8

SEARCH_TERMS = [
    "construction site",
    "living room interior",
    "nature landscape",
    "people walking",
    "office work",
    "cooking kitchen",
    "animals wildlife",
    "gym workout"
]

def sanitize_term(term: str) -> str:
    return term.strip().lower().replace(" ", "_")

def fetch_videos_for_term(term: str, per_page: int = 15):
    params = {
        "key": PIXABAY_API_KEY,
        "q": term,
        "per_page": per_page,
        "safesearch": "true"
    }
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AssetVault-DAM/1.0"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                return data.get("hits", [])
    except Exception as e:
        print(f"Error querying Pixabay for term '{term}': {e}")
    return []

def download_video_file(term: str, hit: dict):
    video_id = hit.get("id")
    videos_info = hit.get("videos", {})
    
    # Select small quality video (fallback to tiny or medium)
    video_source = videos_info.get("small") or videos_info.get("tiny") or videos_info.get("medium")
    if not video_source or not video_source.get("url"):
        return term, video_id, False, "No valid video URL in hit payload"
        
    download_url = video_source["url"]
    clean_term = sanitize_term(term)
    filename = f"{clean_term}_{video_id}.mp4"
    file_path = OUTPUT_DIR / filename
    
    if file_path.exists() and file_path.stat().st_size > 0:
        return term, video_id, True, "already_exists"
        
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AssetVault-DAM/1.0"}
    try:
        req = urllib.request.Request(download_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as res:
            if res.status == 200:
                with open(file_path, "wb") as f:
                    f.write(res.read())
                return term, video_id, True, "downloaded"
    except Exception as e:
        return term, video_id, False, str(e)
        
    return term, video_id, False, "unknown_error"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Starting Pixabay video downloader for {len(SEARCH_TERMS)} categories ({VIDEOS_PER_TERM} videos each)...")
    
    download_tasks = []
    
    for term in SEARCH_TERMS:
        print(f"Fetching metadata for term: '{term}'...")
        hits = fetch_videos_for_term(term, per_page=VIDEOS_PER_TERM + 5)
        selected_hits = hits[:VIDEOS_PER_TERM]
        print(f"-> Found {len(hits)} hits, queued top {len(selected_hits)} for download.")
        
        for hit in selected_hits:
            download_tasks.append((term, hit))
            
    print(f"\nStarting parallel download of {len(download_tasks)} video files...")
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_video_file, term, hit): (term, hit.get("id")) for term, hit in download_tasks}
        
        for future in concurrent.futures.as_completed(futures):
            term, video_id, success, status_msg = future.result()
            if success:
                if status_msg == "downloaded":
                    downloaded += 1
                    print(f"[OK] Downloaded: {sanitize_term(term)}_{video_id}.mp4")
                else:
                    skipped += 1
                    print(f"[SKIP] Already exists: {sanitize_term(term)}_{video_id}.mp4")
            else:
                failed += 1
                print(f"[ERR] Failed {sanitize_term(term)}_{video_id}: {status_msg}")
                
    print(f"\nVideo Download Complete: {downloaded} downloaded, {skipped} skipped, {failed} failed.")

if __name__ == "__main__":
    main()
