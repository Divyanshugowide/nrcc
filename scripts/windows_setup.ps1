\
# PowerShell helper — run from project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Virtual environment created and requirements installed."
Write-Host "Place Arabic PDFs into data\raw_pdfs and run the scripts in order:"
Write-Host " python scripts\02_extract_and_chunk.py"
Write-Host " python scripts\03_build_bm25.py"
Write-Host " python scripts\04_build_faiss.py"
