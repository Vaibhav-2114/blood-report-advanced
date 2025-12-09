# Quick Start: Run Locally Before Deploying

## Prerequisites
- Python 3.9+
- Virtual environment activated
- All dependencies installed from `backend/requirements.txt`

## Running Locally (Two Terminals)

### Terminal 1: Start Backend (FastAPI)
```bash
cd d:\blood-report-advanced
& .\venv\Scripts\Activate.ps1
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at: http://localhost:8000
API docs available at: http://localhost:8000/docs

### Terminal 2: Start Frontend (Streamlit)
```bash
cd d:\blood-report-advanced
& .\venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

Frontend opens at: http://localhost:8501

## Test the App Locally
1. Navigate to http://localhost:8501
2. Upload a blood report image or PDF
3. Verify OCR extracts parameters correctly
4. Click "Analyze" to see results
5. Test Dark Mode toggle (if implemented)

## Verify Everything Works Before Deploying
✅ File upload succeeds
✅ OCR extracts data
✅ Analysis completes without timeouts
✅ Disease predictions display
✅ Dark/Light mode toggles correctly
✅ No errors in terminal/browser console

## Troubleshooting

### "tesseract is not installed"
- Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- For Windows: https://github.com/UB-Mannheim/tesseract/wiki/Downloads

### "timeout" errors during upload
- Increase timeout in frontend/app.py
- Check backend logs for processing delays
- Optimize image size (reduce resolution before OCR)

### "ModuleNotFoundError"
- Ensure virtualenv is activated
- Reinstall dependencies: `pip install -r backend/requirements.txt`

## Ready to Deploy?
See `DEPLOYMENT_GUIDE.md` for step-by-step deployment instructions.
