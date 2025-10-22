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
    """Highlight exact matches (yellow) and semantic/synonym matches (green) showing actual found words."""
    # Store original text for comparison
    original_text = text
    
    # Combine and clean all terms
    all_yellow_terms = []
    for term in yellow_terms:
        if term and len(term.strip()) > 1:
            all_yellow_terms.append(term.strip())
            # Add partial matches for compound terms
            if len(term.strip()) > 4:
                words = term.split()
                if len(words) > 1:
                    all_yellow_terms.extend([w for w in words if len(w) > 2])
    
    all_green_terms = []
    for term in green_terms:
        if term and len(term.strip()) > 1:
            all_green_terms.append(term.strip())
            # Add partial matches for compound terms
            if len(term.strip()) > 4:
                words = term.split()
                if len(words) > 1:
                    all_green_terms.extend([w for w in words if len(w) > 2])
    
    # First pass: yellow highlights for exact query matches
    yellow_positions = []
    for term in sorted(set(all_yellow_terms), key=len, reverse=True):
        if not term.strip(): continue
        
        # Try both exact match and word boundary match
        patterns = [
            re.compile(re.escape(term), re.IGNORECASE),
            re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        ]
        
        for pattern in patterns:
            try:
                for match in pattern.finditer(text):
                    # Use the actual matched text (preserves original case)
                    actual_match = text[match.start():match.end()]
                    # Avoid duplicates
                    pos_key = (match.start(), match.end())
                    if not any(pos_key == (start, end) for start, end, _ in yellow_positions):
                        yellow_positions.append((match.start(), match.end(), actual_match))
            except re.error:
                continue
    
    # Second pass: green highlights for semantic matches (avoid overlap with yellow)
    green_positions = []
    for term in sorted(set(all_green_terms), key=len, reverse=True):
        if not term.strip(): continue
        
        # Skip if this term is already in yellow terms
        if any(normalize_ar(term) == normalize_ar(y_term) for y_term in all_yellow_terms):
            continue
        
        # Try both exact match and word boundary match
        patterns = [
            re.compile(re.escape(term), re.IGNORECASE),
            re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        ]
        
        for pattern in patterns:
            try:
                for match in pattern.finditer(original_text):
                    start, end = match.start(), match.end()
                    
                    # Check if this position overlaps with any yellow highlight
                    overlaps = any(start < y_end and end > y_start for y_start, y_end, _ in yellow_positions)
                    if not overlaps:
                        # Use the actual matched text (preserves original case and form)
                        actual_match = original_text[start:end]
                        # Avoid duplicates
                        pos_key = (start, end)
                        if not any(pos_key == (s, e) for s, e, _ in green_positions):
                            green_positions.append((start, end, actual_match))
            except re.error:
                continue
    
    # If no highlights found, try more aggressive partial matching
    if not yellow_positions and not green_positions:
        # Try partial matches with common words
        common_terms = all_yellow_terms + all_green_terms
        for term in common_terms[:10]:  # Limit to avoid performance issues
            if len(term) > 3:
                # Try finding any part of the term
                for i in range(len(term) - 2):
                    for j in range(i + 3, len(term) + 1):
                        subterm = term[i:j]
                        if len(subterm) > 2:
                            pattern = re.compile(re.escape(subterm), re.IGNORECASE)
                            for match in pattern.finditer(original_text):
                                actual_match = original_text[match.start():match.end()]
                                green_positions.append((match.start(), match.end(), actual_match))
                                break  # Only first match per subterm
                    if green_positions:  # Found something, stop searching
                        break
            if green_positions:
                break
    
    # Sort all positions by start index (reverse order for replacement)
    all_highlights = [
        (start, end, f'<mark style="background:linear-gradient(135deg, #fef08a, #fde047); color:#854d0e; border:1px solid #eab308;" title="Direct match: {found_word}">{found_word}</mark>')
        for start, end, found_word in yellow_positions
    ] + [
        (start, end, f'<mark style="background:linear-gradient(135deg, #bbf7d0, #86efac); color:#14532d; border:1px solid #22c55e;" title="Semantic match: {found_word}">{found_word}</mark>')
        for start, end, found_word in green_positions
    ]
    
    # Remove overlapping highlights (keep longer ones)
    filtered_highlights = []
    for highlight in sorted(all_highlights, key=lambda x: x[1] - x[0], reverse=True):
        start, end, replacement = highlight
        overlaps = any(start < f_end and end > f_start for f_start, f_end, _ in filtered_highlights)
        if not overlaps:
            filtered_highlights.append(highlight)
    
    # Sort by position (reverse order for safe replacement)
    filtered_highlights.sort(key=lambda x: x[0], reverse=True)
    
    # Apply highlights
    result = original_text
    for start, end, replacement in filtered_highlights:
        result = result[:start] + replacement + result[end:]
    
    return result


def load_glossary(path="conf/glossary_ar.json") -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def expand_terms_from_glossary(query: str, glossary: dict) -> list[str]:
    """Return semantically related terms from glossary with better matching."""
    q_tokens = tokenize_ar(query)
    q_normalized = normalize_ar(query)
    original_query = query.strip().lower()
    expanded = []
    
    # Direct term matching with more flexible criteria
    for main_term, synonyms in glossary.items():
        norm_main_term = normalize_ar(main_term)
        norm_syns = [normalize_ar(s) for s in synonyms]
        
        # Check if query contains the main term or its synonyms
        main_term_matches = any(
            token in norm_main_term or norm_main_term in q_normalized or 
            token in main_term.lower() or main_term.lower() in original_query
            for token in q_tokens
        )
        
        synonym_matches = any(
            any(token in norm_syn or norm_syn in token or 
                token in syn.lower() or syn.lower() in original_query
                for token in q_tokens)
            for norm_syn, syn in zip(norm_syns, synonyms)
        )
        
        # Also check partial matches for longer terms
        partial_matches = False
        if len(original_query) > 4:
            partial_matches = (
                original_query in main_term.lower() or main_term.lower() in original_query or
                any(original_query in syn.lower() or syn.lower() in original_query 
                    for syn in synonyms if len(syn) > 3)
            )
        
        if main_term_matches or synonym_matches or partial_matches:
            # Add both the main term and all synonyms
            expanded.append(main_term)
            expanded.extend(synonyms)
            
            # Add word parts for compound terms
            if ' ' in main_term:
                expanded.extend([word for word in main_term.split() if len(word) > 2])
            for syn in synonyms:
                if ' ' in syn:
                    expanded.extend([word for word in syn.split() if len(word) > 2])
    
    # Add common legal/nuclear terms that might be semantically related
    common_legal_terms = {
        'treaty': ['اتفاقية', 'معاهدة', 'اتفاق', 'ميثاق', 'عقد'],
        'agreement': ['اتفاقية', 'اتفاق', 'معاهدة', 'عقد'],
        'obligation': ['التزام', 'التزامات', 'واجب', 'واجبات'],
        'responsibility': ['مسؤولية', 'مسؤوليات'],
        'compensation': ['تعويض', 'تعويضات'],
        'license': ['ترخيص', 'تراخيص', 'رخصة', 'إذن'],
        'nuclear': ['نووي', 'ذري', 'نووية', 'ذرية'],
        'radiation': ['إشعاع', 'إشعاعي', 'إشعاعية'],
        'safety': ['أمان', 'أمن', 'سلامة'],
        'authority': ['هيئة', 'سلطة', 'جهة'],
        'regulation': ['نظام', 'لائحة', 'تنظيم'],
        'اتفاقية': ['treaty', 'agreement', 'معاهدة', 'اتفاق', 'عقد'],
        'التزام': ['obligation', 'واجب', 'التزامات'],
        'مسؤولية': ['responsibility', 'مسؤوليات'],
        'ترخيص': ['license', 'رخصة', 'إذن', 'تراخيص'],
        'نووي': ['nuclear', 'ذري', 'نووية'],
        'هيئة': ['authority', 'سلطة', 'جهة']
    }
    
    # Check common terms
    for term_key, term_synonyms in common_legal_terms.items():
        if (term_key.lower() in original_query or original_query in term_key.lower() or
            any(token in term_key.lower() for token in q_tokens)):
            expanded.extend(term_synonyms)
    
    # Remove duplicates and filter out very short terms
    unique_expanded = []
    for term in expanded:
        term_clean = term.strip()
        if len(term_clean) > 1 and term_clean not in unique_expanded:
            unique_expanded.append(term_clean)
    
    # Limit to reasonable number to avoid performance issues
    return unique_expanded[:50]


# --------------------------- Core Search ---------------------------

def search(indices: Indices, query: str, roles: list[str],
           topk=5, bm25_k=50, vec_k=50, alpha=0.7):

    q_tokens = tokenize_ar(query)
    q_norm = normalize_ar(query)
    original_query = query.strip()

    # Load glossary
    glossary = load_glossary()

    # Expand with semantic synonyms
    green_terms = expand_terms_from_glossary(query, glossary)
    
    # Create comprehensive yellow terms (direct matches)
    yellow_terms = list(set(q_tokens + [original_query]))
    
    # Add English-Arabic cross matches if query is in English
    if re.match(r'^[a-zA-Z\s]+$', original_query.strip()):
        # Query is in English, look for Arabic translations in glossary
        english_query = original_query.lower()
        for main_term, synonyms in glossary.items():
            if any(english_query in syn.lower() or syn.lower() in english_query 
                   for syn in synonyms if re.match(r'^[a-zA-Z\s]+$', syn)):
                yellow_terms.extend([main_term] + synonyms)
    
    # Add Arabic-English cross matches if query is in Arabic
    elif re.match(r'^[\u0600-\u06FF\s]+$', original_query.strip()):
        # Query is in Arabic, look for English translations
        for main_term, synonyms in glossary.items():
            if (original_query in main_term or main_term in original_query or
                any(original_query in syn or syn in original_query for syn in synonyms)):
                # Add English synonyms to yellow terms
                english_synonyms = [syn for syn in synonyms if re.match(r'^[a-zA-Z\s]+$', syn)]
                yellow_terms.extend(english_synonyms)

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

        # RBAC filter - check document-level access
        doc_roles = meta.get("roles", [])
        if roles and not (set(roles) & set(doc_roles)):
            continue

        snippet = meta["text"][:700].replace("\n", " ")
        highlighted = highlight_text(snippet, yellow_terms=yellow_terms, green_terms=green_terms)

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
