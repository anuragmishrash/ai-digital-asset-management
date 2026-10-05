import os
import csv
import urllib.request
import concurrent.futures
from pathlib import Path
from tqdm import tqdm

DEFAULT_TSV_PATH = r"C:\Users\itsan\Downloads\unsplash-research-dataset-lite-latest\photos.tsv000"
OUTPUT_DIR = Path("dataset/images")
METADATA_FILE = OUTPUT_DIR / "_metadata.csv"
TARGET_IMAGE_COUNT = 500
MAX_WORKERS = 16

def download_single_image(row_data):
    photo_id, photo_image_url, photo_description, ai_description = row_data
    file_path = OUTPUT_DIR / f"{photo_id}.jpg"
    
    if file_path.exists() and file_path.stat().st_size > 0:
        return photo_id, True, photo_description, ai_description, "already_exists"
        
    url = f"{photo_image_url}?w=800&auto=format"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AssetVault-DAM/1.0"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status == 200:
                data = response.read()
                with open(file_path, "wb") as f:
                    f.write(data)
                return photo_id, True, photo_description, ai_description, "downloaded"
    except Exception as e:
        # Gracefully handle download failure
        return photo_id, False, photo_description, ai_description, str(e)
        
    return photo_id, False, photo_description, ai_description, "unknown_error"

def main():
    tsv_path = os.environ.get("UNSPLASH_TSV_PATH", DEFAULT_TSV_PATH)
    if not os.path.exists(tsv_path):
        print(f"Error: TSV file not found at: {tsv_path}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] Reading Unsplash TSV metadata from: {tsv_path}")
    candidates = []
    
    with open(tsv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        if not header:
            print("Error: Empty TSV file")
            return
            
        header_map = {col_name: i for i, col_name in enumerate(header)}
        id_idx = header_map.get("photo_id", 0)
        url_idx = header_map.get("photo_image_url", 2)
        desc_idx = header_map.get("photo_description", 8)
        ai_idx = header_map.get("ai_description", 25)

        for row in reader:
            if len(row) > max(id_idx, url_idx):
                photo_id = row[id_idx].strip()
                photo_image_url = row[url_idx].strip()
                photo_desc = row[desc_idx].strip() if len(row) > desc_idx else ""
                ai_desc = row[ai_idx].strip() if len(row) > ai_idx else ""
                
                if photo_id and photo_image_url:
                    candidates.append((photo_id, photo_image_url, photo_desc, ai_desc))
                    if len(candidates) >= TARGET_IMAGE_COUNT * 2:
                        break

    print(f"[2/3] Selected {len(candidates)} candidate rows. Downloading up to {TARGET_IMAGE_COUNT} images...")
    
    successful_records = []
    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_single_image, item): item for item in candidates}
        
        for future in concurrent.futures.as_completed(futures):
            photo_id, success, photo_description, ai_description, status_msg = future.result()
            
            if success:
                successful_records.append({
                    "photo_id": photo_id,
                    "photo_description": photo_description,
                    "ai_description": ai_description
                })
                if status_msg == "downloaded":
                    downloaded_count += 1
                else:
                    skipped_count += 1
            else:
                failed_count += 1
                
            if len(successful_records) >= TARGET_IMAGE_COUNT:
                # Cancel remaining tasks
                for f_pending in futures:
                    f_pending.cancel()
                break

    print(f"\n[3/3] Download Summary: {downloaded_count} newly downloaded, {skipped_count} skipped (already exists), {failed_count} failed.")

    # Save metadata CSV
    print(f"Saving metadata to {METADATA_FILE}...")
    with open(METADATA_FILE, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["photo_id", "photo_description", "ai_description"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in successful_records[:TARGET_IMAGE_COUNT]:
            writer.writerow(record)
            
    print(f"Successfully processed and saved {len(successful_records[:TARGET_IMAGE_COUNT])} image records to {METADATA_FILE}.")

if __name__ == "__main__":
    main()
