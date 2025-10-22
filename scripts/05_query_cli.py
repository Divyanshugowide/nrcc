import argparse
from app.retrieval import load_bm25, load_faiss, load_meta, load_model, Indices, search
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help="Arabic question")
    ap.add_argument("--roles", nargs="+", default=["staff"])
    ap.add_argument("--topk", type=int, default=5)
    a = ap.parse_args()
    bm25 = load_bm25("data/idx/bm25.pkl")
    faiss_index = load_faiss("data/idx/mE5.faiss")
    meta = load_meta("data/idx/meta.json")
    model = load_model("intfloat/multilingual-e5-base")
    idx = Indices(bm25=bm25, faiss_index=faiss_index, meta=meta, model=model)
    out = search(idx, a.query, roles=a.roles, topk=a.topk)
    print("ANSWER:\n", out["answer"])
    print("\nCITATIONS:")
    for c in out["results"]:
        print(f"- {c['doc_id']} | المادة {c['article_no']} | ص{c['page_start']}-{c['page_end']} | score={c['score']:.3f}")
        print(f"  {c['excerpt'][:200]}...")
