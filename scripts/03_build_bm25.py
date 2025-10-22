import json, pickle, os
from rank_bm25 import BM25Okapi
from app.normalize import tokenize_ar
INP = "data/processed/chunks.jsonl"
OUT = "data/idx/bm25.pkl"
def load_chunks(path):
    return [json.loads(line) for line in open(path, "r", encoding="utf-8")]
if __name__ == "__main__":
    chunks = load_chunks(INP)
    docs_tokens = [tokenize_ar(ch["text"]) for ch in chunks]
    bm25 = BM25Okapi(docs_tokens)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "wb") as f:
        pickle.dump(bm25, f)
    print(f"[ok] wrote {OUT} over {len(chunks)} chunks")
