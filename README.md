# Blood Report Analyzer — Advanced ML Project

An AI-powered blood report analysis system with Tesseract OCR, FastAPI backend, and Streamlit frontend. Extracts blood parameters, compares against normal ranges, and predicts possible diseases using rule-based logic.

## 🚀 Quick Start

### Local Development (2 Steps)

**Option A: Using Batch Script (Windows)**
```bash
start-local.bat
```

**Option B: Manual Setup**

Terminal 1 - Backend:
```bash
venv\Scripts\activate
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 - Frontend:
```bash
venv\Scripts\activate
streamlit run frontend/app.py
```

Then open: http://localhost:8501

### System Requirements

- Python 3.9+
- Tesseract OCR (Windows: https://github.com/UB-Mannheim/tesseract/wiki)
- For PDF support: install `poppler` (optional, PyPDF2 fallback available)

### Initial Setup

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run locally (see Quick Start above)

4. (Optional) Train model:
   ```bash
   python ml_model/train_model.py
   ```
   This generates a trained model at `backend/api/services/predict_model.pkl`.

5. Start backend:
   ```bash
   uvicorn backend.api.main:app --reload --port 8000
   ```

6. In another terminal, run frontend:
   ```bash
   streamlit run frontend/app.py
   ```

Open Streamlit at http://localhost:8501
FastAPI docs at http://127.0.0.1:8000/docs
