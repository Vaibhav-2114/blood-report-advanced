# Blood Report Analyzer — Advanced ML Project

This project contains a FastAPI backend, Streamlit frontend, OCR extraction, and an ML model for risk prediction.

## How to run (Windows recommended steps)

1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install backend requirements:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. (Optional) Install Tesseract OCR on system:
   - Windows: https://github.com/tesseract-ocr/tesseract/wiki
   - Make sure `tesseract` is on PATH.

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
