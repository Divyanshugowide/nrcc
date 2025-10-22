from __future__ import annotations
import json, pickle, faiss, numpy as np
from typing import List
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from .normalize import tokenize_ar, normalize_ar

@dataclass
class Indices:
    bm25: BM25Okapi
    faiss_index: faiss.Index
    meta: list[dict]
    model: SentenceTransformer

def load_bm25(path): return pickle.load(open(path,"rb"))
def load_faiss(path): return faiss.read_index(path)
def load_meta(path):  return json.load(open(path,"r",encoding="utf-8"))
def load_model(name="intfloat/multilingual-e5-base"): return SentenceTransformer(name)

def minmax_norm(a: np.ndarray) -> np.ndarray:
    if a.size == 0: return a
    mn, mx = a.min(), a.max()
    return np.zeros_like(a) if mx-mn<1e-9 else (a-mn)/(mx-mn)

def search(indices: Indices, query: str, roles: list[str], topk=5, bm25_k=50, vec_k=50, alpha=0.6):
    q_tokens = tokenize_ar(query)
    bm25_scores = indices.bm25.get_scores(q_tokens)
    bm25_ranks = np.argsort(bm25_scores)[::-1][:bm25_k]
    q_emb = indices.model.encode([normalize_ar(query)], normalize_embeddings=True)
    D, I = indices.faiss_index.search(np.asarray(q_emb, dtype="float32"), vec_k)
    vec_ranks, vec_scores = I[0], D[0]
    cand_ids = list(set(bm25_ranks.tolist()) | set(vec_ranks.tolist()))
    bm = np.array([bm25_scores[i] for i in cand_ids])
    vec_ranks_list = vec_ranks.tolist() if hasattr(vec_ranks, "tolist") else vec_ranks
    vc = np.array([vec_scores[vec_ranks_list.index(i)] if i in vec_ranks_list else 0.0 for i in cand_ids])
    bm_n, vc_n = minmax_norm(bm), minmax_norm(vc)
    final = alpha*vc_n + (1-alpha)*bm_n
    order = np.argsort(final)[::-1]
    results = []
    for j in order:
        idx = cand_ids[j]
        meta = indices.meta[idx]
        if roles and not (set(roles) & set(meta.get("roles",[]))):  # RBAC filter
            continue
        excerpt = meta["text"][:400].replace("\n"," ").strip()
        results.append({
            "doc_id": meta["doc_id"],
            "article_no": meta.get("article_no"),
            "page_start": meta.get("page_start"),
            "page_end": meta.get("page_end"),
            "score": float(final[j]),
            "excerpt": excerpt
        })
        if len(results) >= topk: break
    answer = results[0]["excerpt"] if results else "لم يتم العثور على نتيجة ذات صلة مع الاستشهاد."
    return {"answer": answer, "results": results}
