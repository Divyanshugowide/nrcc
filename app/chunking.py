from __future__ import annotations
import fitz, re, json, os
from typing import List
from .normalize import normalize_ar, to_western_digits, tokenize_ar

ARTICLE_RE = re.compile(
    r'(?:^|\n)\s*(?:المادة|مادة)\s*([0-9\u0660-\u0669\u06F0-\u06F9]+|\S+)\s*', re.M
)

def extract_text_with_pages(pdf_path: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    return [{"page": i+1, "text": page.get_text("text")} for i, page in enumerate(doc)]

def split_by_articles(full_text: str) -> list[dict]:
    """Split PDF full text by Arabic article markers."""
    positions = []
    for m in ARTICLE_RE.finditer(full_text):
        num = to_western_digits(m.group(1))
        positions.append((m.start(), num))
    chunks = []
    if not positions:
        return [{"article_no": None, "text": full_text}]
    for idx, (start, num) in enumerate(positions):
        end = positions[idx+1][0] if idx+1 < len(positions) else len(full_text)
        chunks.append({"article_no": num, "text": full_text[start:end].strip()})
    return chunks

def find_pages_for_text(article_text: str, pages: list[dict]) -> list[int]:
    """Find all pages that contain any portion of this article text."""
    normalized = normalize_ar(article_text[:300])
    hits = []
    for p in pages:
        if normalized[:40] in normalize_ar(p["text"]):
            hits.append(p["page"])
    return hits or [1]

def build_chunks_from_pdf(pdf_path: str, doc_id: str, roles: list[str]) -> list[dict]:
    """Build semantic chunks with better metadata."""
    pages = extract_text_with_pages(pdf_path)
    full_text = "\n".join([p["text"] for p in pages])
    article_chunks = split_by_articles(full_text)
    out = []

    for i, ch in enumerate(article_chunks):
        page_hits = find_pages_for_text(ch["text"], pages)
        tokens = tokenize_ar(ch["text"])
        out.append({
            "id": f"{doc_id}::art{ch['article_no'] or i}",
            "doc_id": doc_id,
            "article_no": ch["article_no"],
            "pages": page_hits,
            "text": ch["text"],
            "norm_text": normalize_ar(ch["text"]),
            "roles": roles,
            "tokens": list(set(tokens))
        })
    return out

def run_for_folder(raw_dir: str, out_path: str, default_roles: list[str]|None=None) -> None:
    default_roles = default_roles or ["staff","legal","admin"]
    all_chunks = []
    for fn in sorted(os.listdir(raw_dir)):
        if fn.lower().endswith(".pdf"):
            doc_id = os.path.splitext(fn)[0]
            print(f"[+] Processing {fn}")
            all_chunks += build_chunks_from_pdf(os.path.join(raw_dir, fn), doc_id, default_roles)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for ch in all_chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")
    print(f"[ok] wrote {len(all_chunks)} chunks → {out_path}")
