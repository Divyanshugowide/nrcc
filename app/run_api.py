from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
import os, json
from .retrieval import load_bm25, load_faiss, load_meta, load_model, Indices, search

# ---- Paths ----
BM25_PATH = "data/idx/bm25.pkl"
FAISS_PATH = "data/idx/mE5.faiss"
META_PATH = "data/idx/meta.json"
MODEL_NAME = "intfloat/multilingual-e5-base"

app = FastAPI(title="Arabic Legal Q&A")

indices: Indices | None = None


class AskPayload(BaseModel):
    user_id: str
    roles: list[str] = ["staff"]
    query: str
    topk: int = 5


@app.on_event("startup")
def load_all():
    global indices
    print("[Loading BM25 + FAISS + model...]")
    bm25 = load_bm25(BM25_PATH)
    faiss_index = load_faiss(FAISS_PATH)
    meta = load_meta(META_PATH)
    model = load_model(MODEL_NAME)
    indices = Indices(bm25=bm25, faiss_index=faiss_index, meta=meta, model=model)
    print("[OK] System ready ✅")


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>🔍 الباحث القانوني النووي ⚖️</title>
<style>
body { font-family: 'Segoe UI', sans-serif; background: #f5f6fa; direction: rtl; text-align: right; padding: 40px; }
.container { max-width: 900px; margin: auto; background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
mark { padding: 2px 4px; border-radius: 3px; font-weight: bold; }
mark[style*="yellow"] { background: #fff176; }
mark[style*="lightgreen"] { background: #a5d6a7; }
#answer, #citations div { line-height: 1.7; font-size: 1.05em; margin-top: 10px; }
</style>
</head>
<body>
<div class="container">
  <h1>🔍 الباحث القانوني النووي</h1>
  <p>اسأل سؤالاً حول الأنظمة النووية أو القوانين:</p>
  <div style="display:flex;gap:10px;">
    <input id="query" style="flex:1;padding:8px;" placeholder="مثال: ما هي الاتفاقيات النووية؟">
    <button onclick="askQuestion()" style="padding:8px 15px;background:#005baa;color:white;border:none;border-radius:6px;">إرسال</button>
  </div>
  <div id="loading" style="display:none;color:#005baa;margin-top:10px;">⏳ جارٍ البحث...</div>
  <h3>الجواب:</h3>
  <div id="answer"></div>
  <h3>النتائج:</h3>
  <div id="citations"></div>
</div>

<script>
async function askQuestion() {
  const query = document.getElementById("query").value.trim();
  const ans = document.getElementById("answer");
  const cites = document.getElementById("citations");
  const loading = document.getElementById("loading");

  if (!query) { alert("يرجى إدخال سؤال أولاً"); return; }

  ans.innerHTML = "";
  cites.innerHTML = "";
  loading.style.display = "block";

  const payload = { user_id: "demo", roles: ["staff"], query: query, topk: 5 };

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const text = await res.text();  // ✅ Receive raw text
    const data = JSON.parse(text);  // ✅ Parse manually

    loading.style.display = "none";
    ans.innerHTML = data.answer || "لم يتم العثور على نتيجة ذات صلة.";

    if (data.citations && data.citations.length > 0) {
      data.citations.forEach(c => {
        const div = document.createElement("div");
        div.innerHTML = `<b>📘 ${c.doc_id}</b> | المادة ${c.article_no || "?"} | الصفحة ${c.page_start || "?"}-${c.page_end || "?"}<br>${c.excerpt}`;
        cites.appendChild(div);
      });
    }
  } catch (err) {
    console.error(err);
    ans.innerHTML = "حدث خطأ أثناء المعالجة.";
    loading.style.display = "none";
  }
}
</script>
</body></html>
""")


@app.post("/ask", response_class=Response)
async def ask(payload: AskPayload):
    """
    Return manual JSON string (NOT auto-escaped).
    """
    out = search(indices, payload.query, payload.roles, topk=payload.topk)
    raw_json = json.dumps({"answer": out["answer"], "citations": out["results"]}, ensure_ascii=False)
    # ✅ return as plain response so <mark> isn't escaped
    return Response(content=raw_json, media_type="application/json")
