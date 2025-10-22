from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os

from .retrieval import load_bm25, load_faiss, load_meta, load_model, Indices, search

# --- Paths ---
BM25_PATH = os.getenv("BM25_PATH", "data/idx/bm25.pkl")
FAISS_PATH = os.getenv("FAISS_PATH", "data/idx/mE5.faiss")
META_PATH = os.getenv("META_PATH", "data/idx/meta.json")
MODEL_NAME = os.getenv("MODEL_NAME", "intfloat/multilingual-e5-base")

app = FastAPI(title="Arabic Legal Q&A")

indices: Indices | None = None


class AskPayload(BaseModel):
    user_id: str
    roles: list[str] = ["staff"]
    query: str
    topk: int = 5


@app.on_event("startup")
def _load():
    """Load all models and indexes on startup"""
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
    """Serve embedded Arabic Q&A web app"""
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>الباحث القانوني النووي ⚖️</title>
<style>
body {
  font-family: 'Segoe UI', sans-serif;
  background: #f5f6fa;
  margin: 0; padding: 0;
  direction: rtl; text-align: right;
}
.container {
  max-width: 900px;
  margin: 50px auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  padding: 30px;
}
h1 { color: #005baa; text-align: center; }
.controls {
  display: flex; gap: 10px; margin: 20px 0;
}
.controls select, .controls input, .controls button {
  padding: 10px; font-size: 1em; border-radius: 6px; border: 1px solid #ccc;
}
.controls button {
  background: #005baa; color: white; cursor: pointer;
}
.controls button:hover { background: #004080; }
#answer {
  background: #eaf6ff; padding: 15px; border-radius: 8px; line-height: 1.6; min-height: 60px;
}
#citations li {
  background: #f0f0f0; margin: 5px 0; padding: 10px;
  border-radius: 6px; font-size: 0.95em; list-style-type: none;
}
#loading {
  display: none; color: #005baa; font-weight: bold;
}
.footer {
  text-align: center; margin-top: 40px; font-size: 0.9em; color: #555;
}
</style>
</head>
<body>
  <div class="container">
    <h1>🔍 الباحث القانوني النووي</h1>
    <p>اسأل سؤالاً حول الأنظمة النووية أدناه:</p>

    <div class="controls">
      <select id="role">
        <option value="staff">موظف</option>
        <option value="legal">قانوني</option>
        <option value="admin">مسؤول</option>
        <option value="inspector">مفتش</option>
      </select>
      <input type="text" id="query" placeholder="مثال: ما هو حد مسؤولية المشغل؟" style="flex:1;">
      <button onclick="askQuestion()">إرسال</button>
    </div>

    <div id="loading">⏳ جارٍ البحث...</div>

    <div id="output">
      <h3>الجواب:</h3>
      <div id="answer"></div>

      <h3>الاستشهادات:</h3>
      <ul id="citations"></ul>
    </div>

    <div class="footer">
      يعمل بالكامل دون إنترنت 🌐 — بإشراف الهيئة الوطنية للرقابة النووية
    </div>
  </div>

<script>
async function askQuestion() {
  const query = document.getElementById("query").value.trim();
  const role = document.getElementById("role").value;
  const ans = document.getElementById("answer");
  const cites = document.getElementById("citations");
  const loading = document.getElementById("loading");
  if (!query) { alert("يرجى إدخال سؤال أولاً"); return; }

  ans.innerHTML = "";
  cites.innerHTML = "";
  loading.style.display = "block";

  const payload = { user_id: "demo", roles: [role], query: query, topk: 5 };

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    loading.style.display = "none";
    ans.innerHTML = data.answer || "لم يتم العثور على نتيجة ذات صلة.";
    cites.innerHTML = "";
    if (data.citations && data.citations.length > 0) {
      data.citations.forEach(c => {
        const li = document.createElement("li");
        li.innerHTML = `📘 <b>${c.doc_id}</b> — المادة ${c.article_no || "غير محددة"} — ص${c.page_start}-${c.page_end}`;
        cites.appendChild(li);
      });
    } else {
      cites.innerHTML = "<li>لا توجد استشهادات متاحة</li>";
    }
  } catch (err) {
    loading.style.display = "none";
    ans.innerHTML = "حدث خطأ أثناء المعالجة.";
    console.error(err);
  }
}
</script>
</body>
</html>
""")


@app.post("/ask")
async def ask(payload: AskPayload):
    out = search(indices, payload.query, payload.roles, topk=payload.topk)
    return JSONResponse(content={"answer": out["answer"], "citations": out["results"]})


@app.get("/health")
def health():
    return {"ok": True}
