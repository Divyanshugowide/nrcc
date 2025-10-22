NRRC Arabic PoV - Offline Arabic Document Retrieval
=================================================

Windows-ready project. Follow these steps:

1. Create & activate virtualenv (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip

2. Install requirements:
   pip install -r requirements.txt

3. Put your Arabic PDFs into:
   data\raw_pdfs\

4. Run the pipeline:
   python scripts\02_extract_and_chunk.py
   python scripts\03_build_bm25.py
   python scripts\04_build_faiss.py

5. Test CLI:
   python scripts\05_query_cli.py --query "ما هو حد مسؤولية المشغل؟" --roles staff

6. Run API:
   uvicorn app.run_api:app --host 0.0.0.0 --port 8000 --reload

Notes:
- First run requires internet to download the sentence-transformers model (intfloat/multilingual-e5-base).
- To run fully offline, cache the model directory and set TRANSFORMERS_CACHE env var or pass a local path to SentenceTransformer().
