from __future__ import annotations
import json, pickle, faiss, numpy as np, re, os
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


# --------------------------- Loaders ---------------------------

def load_bm25(path): return pickle.load(open(path, "rb"))
def load_faiss(path): return faiss.read_index(path)
def load_meta(path): return json.load(open(path, "r", encoding="utf-8"))
def load_model(name="intfloat/multilingual-e5-base"): return SentenceTransformer(name)


# --------------------------- Utilities ---------------------------

def minmax_norm(a: np.ndarray) -> np.ndarray:
    if a.size == 0:
        return a
    mn, mx = a.min(), a.max()
    return np.zeros_like(a) if mx - mn < 1e-9 else (a - mn) / (mx - mn)


def highlight_text(text: str, yellow_terms: list[str], green_terms: list[str]) -> str:
    """Highlight BM25 (yellow) and semantic/synonym (green) matches."""
    for t in sorted(set(yellow_terms), key=len, reverse=True):
        if not t.strip(): continue
        pattern = re.compile(re.escape(t), re.IGNORECASE)
        text = pattern.sub(f'<mark style="background:yellow;">{t}</mark>', text)

    for t in sorted(set(green_terms), key=len, reverse=True):
        if not t.strip(): continue
        # skip if already yellow-highlighted
        if f'<mark style="background:yellow;">{t}</mark>' in text:
            continue
        pattern = re.compile(re.escape(t), re.IGNORECASE)
        text = pattern.sub(f'<mark style="background:lightgreen;">{t}</mark>', text)

    return text


def load_glossary(path="conf/glossary_ar.json") -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def expand_terms_from_glossary(query: str, glossary: dict) -> list[str]:
    """Return all synonyms that appear related to any query term."""
    q_tokens = tokenize_ar(query)
    expanded = []
    for term in glossary:
        norm_term = normalize_ar(term)
        norm_syns = [normalize_ar(s) for s in glossary[term]]
        if any(q in norm_term or q in norm_syns for q in q_tokens):
            expanded += glossary[term]
    return list(set(expanded))


# --------------------------- Core Search ---------------------------

def search(indices: Indices, query: str, roles: list[str],
           topk=5, bm25_k=50, vec_k=50, alpha=0.7):

    q_tokens = tokenize_ar(query)
    q_norm = normalize_ar(query)

    # Load glossary
    glossary = load_glossary()

    # Expand with semantic synonyms
    green_terms = expand_terms_from_glossary(query, glossary)

    # BM25
    bm25_scores = indices.bm25.get_scores(q_tokens)
    bm25_ranks = np.argsort(bm25_scores)[::-1][:bm25_k]

    # FAISS
    q_emb = indices.model.encode([q_norm], normalize_embeddings=True)
    D, I = indices.faiss_index.search(np.asarray(q_emb, dtype="float32"), vec_k)
    vec_ranks, vec_scores = I[0], D[0]

    # Combine
    cand_ids = list(set(bm25_ranks.tolist()) | set(vec_ranks.tolist()))
    bm = np.array([bm25_scores[i] for i in cand_ids])
    vec_ranks_list = vec_ranks.tolist() if hasattr(vec_ranks, "tolist") else vec_ranks
    vc = np.array([vec_scores[vec_ranks_list.index(i)] if i in vec_ranks_list else 0.0 for i in cand_ids])
    bm_n, vc_n = minmax_norm(bm), minmax_norm(vc)
    final = alpha * vc_n + (1 - alpha) * bm_n
    order = np.argsort(final)[::-1]

    results = []
    for j in order:
        idx = cand_ids[j]
        meta = indices.meta[idx]

        # RBAC filter
        if roles and not (set(roles) & set(meta.get("roles", []))):
            continue

        snippet = meta["text"][:700].replace("\n", " ")
        highlighted = highlight_text(snippet, yellow_terms=q_tokens, green_terms=green_terms)

        pages = meta.get("pages", [])
        page_start = pages[0] if pages else meta.get("page_start")
        page_end = pages[-1] if pages else meta.get("page_end")

        results.append({
            "rank": len(results) + 1,
            "doc_id": meta["doc_id"],
            "article_no": meta.get("article_no"),
            "page_start": page_start,
            "page_end": page_end,
            "score": float(final[j]),
            "excerpt": highlighted
        })

        if len(results) >= topk:
            break

    answer_html = results[0]["excerpt"] if results else "لم يتم العثور على نتيجة ذات صلة."
    return {"answer": answer_html, "results": results}
