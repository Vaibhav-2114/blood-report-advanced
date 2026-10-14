# Blood Report Analyzer

A student project that extracts common blood-test values from report images or text-based PDFs, compares values with configured reference ranges, and displays heuristic risk indicators in a Streamlit interface.

> **Medical disclaimer:** This project is for learning and demonstration only. It is not a medical device and does not diagnose disease. OCR and rule-based outputs can be wrong. Use the original lab report and consult a qualified healthcare professional for interpretation.

## Features

- Streamlit interface for uploading reports and reviewing extracted text.
- Tesseract OCR for report images and scanned PDFs.
- PyPDF2 for text extraction from text-based PDFs.
- Regex-based extraction and normalization of common parameters.
- FastAPI endpoints for upload and analysis.
- Reference-range comparison and rule-based risk indicators.
- Optional Random Forest model. The application falls back to rule-based risk indicators when no model is available.

## Project layout

```text
backend/
  api/
    main.py                 FastAPI application
    index.py                Vercel entry point (optional deployment)
    services/               OCR, extraction, comparison and risk logic
    utils/                  Parameter aliases and reference ranges
  requirements.txt          Python dependencies
frontend/
  app.py                    Streamlit user interface
ml_model/
  train_model.py            Generates synthetic demo data and trains a model
utils/sample_reports/        Small sample text report
.streamlit/config.toml       Streamlit theme and local server settings
start-local.bat              Windows helper to start both services
vercel.json                  Optional Vercel API configuration
```

## Requirements

- Python 3.10 or newer (Python 3.11 is a reasonable choice for deployment compatibility).
- Tesseract OCR installed and available on your system PATH.
- Poppler is needed by `pdf2image` only when OCR must be run on scanned PDFs. Text-based PDFs use PyPDF2 first.

## Run locally

### 1. Create a virtual environment

**Windows PowerShell**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux/macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Install system OCR tools

Install Tesseract OCR for your operating system and confirm it is available:
```bash
tesseract --version
```

For scanned PDF files, install Poppler too. If you only need image reports and text-based PDFs, Poppler is not required.

### 3. Start the backend

From the repository root, in terminal 1:
```bash
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
```

Check the API at http://127.0.0.1:8000 and interactive docs at http://127.0.0.1:8000/docs.

### 4. Start the frontend

In terminal 2, with the same environment activated:
```bash
streamlit run frontend/app.py
```

Open http://localhost:8501. The local API URL defaults to `http://127.0.0.1:8000`. For Streamlit secrets, create `.streamlit/secrets.toml` from the example file if you need to override it.

## Optional: train the demo model

```bash
python ml_model/train_model.py
```

This script generates **synthetic** training data and writes a model to `backend/api/services/predict_model.pkl`. This is for software demonstration only; the model is not trained or validated on clinical data and must not be used for medical decisions.

## Dependencies

Install Python dependencies with:
```bash
pip install -r requirements.txt
```

`backend/requirements.txt` is retained for the Vercel API build configuration. Keep the two dependency files aligned when changing dependencies.

## Deployment notes

- The Streamlit UI and FastAPI API are separate services in the recommended deployment layout.
- Vercel's standard Python runtime does not include Tesseract or Poppler by default. Image OCR and scanned-PDF OCR therefore need a runtime that supplies those system dependencies. Text-based PDF extraction may still work.
- Configure the deployed frontend's `api_url` using Streamlit Cloud Secrets. Do not commit real credentials or deployment-specific secrets.
- `vercel.json` is included as an optional backend deployment configuration; verify deployment-specific behavior before relying on it.

## Development checks

```bash
python -m compileall -q backend frontend ml_model
python -c "import json,pathlib; [json.loads(p.read_text()) for p in pathlib.Path('backend/api/utils').glob('*.json')]; print('JSON files OK')"
```

## Limitations

- Parameter extraction is heuristic and may miss, misread, or mislabel values.
- The currently configured ranges are simplified and may not account for age, sex, laboratory methods, or local reference intervals.
- Disease rules and synthetic model outputs are not clinically validated.
- Always check extracted values against the report before interpreting results.
