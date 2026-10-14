# Quick Start

See [README.md](README.md) for full setup instructions.

1. Install Python dependencies: `pip install -r requirements.txt`.
2. Install Tesseract OCR and confirm `tesseract --version` works.
3. Start the API from the repository root:
   ```bash
   python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
   ```
4. In a second terminal, start the UI:
   ```bash
   streamlit run frontend/app.py
   ```
5. Open http://localhost:8501 and test with a report.

For scanned PDFs, install Poppler. The application tries direct PDF text extraction before converting pages to images.
