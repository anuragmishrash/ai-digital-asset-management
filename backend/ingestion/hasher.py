import hashlib
import os

def compute_md5(filepath: str, chunk_size: int = 65536) -> str:
    """
    Compute MD5 hash of a file efficiently by reading in chunks.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found for hashing: {filepath}")
        
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()
