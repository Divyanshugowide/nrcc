import json, os, faiss, numpy as np
from sentence_transformers import SentenceTransformer
INP = "data/processed/chunks.jsonl"
IDX = "data/idx/mE5.faiss"
META = "data/idx/meta.json"
MODEL = os.getenv("MODEL_NAME","intfloat/multilingual-e5-base")
def load_chunks(path):
    return [json.loads(line) for line in open(path, "r", encoding="utf-8")]
if __name__ == "__main__":
    chunks = load_chunks(INP)
    model = SentenceTransformer(MODEL)
    texts = [c["norm_text"] for c in chunks]
    embs = model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=True)
    embs = np.asarray(embs, dtype="float32")
    index = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)
    os.makedirs(os.path.dirname(IDX), exist_ok=True)
    faiss.write_index(index, IDX)
    json.dump(chunks, open(META,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[ok] wrote {IDX} and {META} for {len(chunks)} chunks")
