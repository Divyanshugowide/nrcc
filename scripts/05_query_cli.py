import argparse
from app.retrieval import load_bm25, load_faiss, load_meta, load_model, Indices, search
from app.auth import get_effective_roles, filter_documents_by_access

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help="Arabic question")
    ap.add_argument("--roles", nargs="+", default=["staff"], help="User roles (staff, legal, admin)")
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--show-restricted", action="store_true", help="Show information about restricted documents")
    a = ap.parse_args()
    
    bm25 = load_bm25("data/idx/bm25.pkl")
    faiss_index = load_faiss("data/idx/mE5.faiss")
    meta = load_meta("data/idx/meta.json")
    model = load_model("intfloat/multilingual-e5-base")
    idx = Indices(bm25=bm25, faiss_index=faiss_index, meta=meta, model=model)
    
    # Get effective roles
    effective_roles = get_effective_roles(a.roles)
    print(f"User roles: {a.roles}")
    print(f"Effective roles: {effective_roles}")
    
    # Perform search
    out = search(idx, a.query, roles=effective_roles, topk=a.topk)
    
    # Filter results based on file access restrictions
    filtered_results = filter_documents_by_access(a.roles, out["results"])
    
    print("\nANSWER:")
    if not filtered_results and out["results"]:
        print("لم يتم العثور على نتائج متاحة بناءً على صلاحياتك الحالية.")
    else:
        print(out["answer"])
    
    print(f"\nCITATIONS ({len(filtered_results)} accessible out of {len(out['results'])} total):")
    for c in filtered_results:
        restricted_indicator = " [RESTRICTED]" if "restricted" in c['doc_id'].lower() else ""
        print(f"- {c['doc_id']}{restricted_indicator} | المادة {c['article_no']} | ص{c['page_start']}-{c['page_end']} | score={c['score']:.3f}")
        print(f"  {c['excerpt'][:200]}...")
    
    if a.show_restricted and len(out['results']) > len(filtered_results):
        print(f"\nRESTRICTED DOCUMENTS ({len(out['results']) - len(filtered_results)} hidden):")
        for c in out['results']:
            if c not in filtered_results:
                print(f"- {c['doc_id']} [ACCESS DENIED]")
