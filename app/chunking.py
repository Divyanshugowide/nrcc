from __future__ import annotations
import fitz, re, json, os
from typing import List
from .normalize import normalize_ar, to_western_digits

ARTICLE_RE = re.compile(
    r'(?:^|\n)\s*(?:المادة|مادة)\s*(?:([0-9\u0660-\u0669\u06F0-\u06F9]+)|([اأإآ]?[لح]?[وا]?[حخ]?[ادي]?[ةي]\s?والعشرون|الحادية\s?والعشرون|الثانية\s?والعشرون|الثالثة\s?والعشرون|الرابعة\s?والعشرون|الخامسة\s?والعشرون|السادسة\s?والعشرون|السابعة\s?والعشرون|الثامنة\s?والعشرون|التاسعة\s?والعشرون|الثلاثون))',
    re.M)

def extract_text_with_pages(pdf_path: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    return [{"page": i+1, "text": page.get_text("text")} for i, page in enumerate(doc)]

def split_by_articles(full_text: str) -> list[dict]:
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

def map_article_to_pages(article_text: str, pages: list[dict]) -> tuple[int,int]:
    probe = normalize_ar(article_text[:200])
    first, last = None, None
    for p in pages:
        normp = normalize_ar(p["text"])
        if probe and probe[:50] in normp:
            if first is None: first = p["page"]
            last = p["page"]
    return first or 1, last or first or 1

def build_chunks_from_pdf(pdf_path: str, doc_id: str, roles: list[str]) -> list[dict]:
    pages = extract_text_with_pages(pdf_path)
    full_text = "\n".join([p["text"] for p in pages])
    article_chunks = split_by_articles(full_text)
    out = []
    for i, ch in enumerate(article_chunks):
        p1, p2 = map_article_to_pages(ch["text"], pages)
        out.append({
            "id": f"{doc_id}::art{ch['article_no'] or i}",
            "doc_id": doc_id,
            "article_no": ch["article_no"],
            "page_start": p1,
            "page_end": p2,
            "text": ch["text"],
            "norm_text": normalize_ar(ch["text"]),
            "roles": roles
        })
    return out

def run_for_folder(raw_dir: str, out_path: str, default_roles: list[str]|None=None) -> None:
    default_roles = default_roles or ["staff","legal","admin"]
    all_chunks = []
    for fn in sorted(os.listdir(raw_dir)):
        if fn.lower().endswith(".pdf"):
            doc_id = os.path.splitext(fn)[0]
            all_chunks += build_chunks_from_pdf(os.path.join(raw_dir, fn), doc_id, default_roles)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for ch in all_chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")
