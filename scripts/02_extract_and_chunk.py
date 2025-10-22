import os
from app.chunking import run_for_folder
RAW = "data/raw_pdfs"
OUT = "data/processed/chunks.jsonl"
if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    run_for_folder(RAW, OUT)  # default roles: staff, legal, admin
    print(f"[ok] wrote {OUT}")
