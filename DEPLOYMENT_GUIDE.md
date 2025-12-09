# Deployment Guide: Blood Report Analyzer on Vercel

## Architecture Overview

Your application has two components:
1. **Frontend**: Streamlit app (interactive UI)
2. **Backend**: FastAPI server (OCR, analysis, disease prediction)

### Deployment Strategy

Since Vercel has limitations with long-running processes like Streamlit servers, here are the recommended approaches:

---

## Option 1: Deploy Backend on Vercel + Frontend on Streamlit Cloud (RECOMMENDED)

### Advantages
- ✅ Best performance and simplicity
- ✅ Streamlit Cloud is designed for Streamlit apps
- ✅ FastAPI runs reliably on Vercel Serverless Functions
- ✅ Easy to maintain and update both separately

### Steps

#### A. Deploy Backend (FastAPI) to Vercel

**1. Create a Vercel project:**
```bash
cd d:\blood-report-advanced
npm init -y
npm install --save-dev vercel
```

**2. Create `vercel.json` in root:**
```json
{
  "builds": [
    {
      "src": "backend/api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/api/main.py"
    }
  ],
  "env": {
    "PYTHONUNBUFFERED": "1"
  }
}
```

**3. Create `backend/api/wsgi.py`:**
```python
from main import app

# For Vercel
handler = app
```

**4. Deploy to Vercel:**
```bash
npx vercel --prod
```

**5. Copy the deployed URL (e.g., `https://your-project.vercel.app`)**

#### B. Deploy Frontend (Streamlit) to Streamlit Cloud

**1. Push your code to GitHub:**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

**2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)**

**3. Click "New app" and select your GitHub repository**

**4. Set the main file path: `frontend/app.py`**

**5. In "Advanced settings", add this Environment Variable:**
```
API_URL=https://your-vercel-project.vercel.app
```

**6. Deploy!**

---

## Option 2: Deploy Both on Render (Alternative)

If you prefer a simpler single-platform approach:

### Backend on Render
1. Push code to GitHub
2. Create new "Web Service" on render.com
3. Connect your GitHub repository
4. Set build command: `pip install -r backend/requirements.txt`
5. Set start command: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`

### Frontend on Streamlit Cloud
(Same as Option 1, Step B)

---

## Option 3: Deploy Everything on AWS / Google Cloud (Advanced)

For production with more control:
- Use AWS Lambda + API Gateway for backend (FastAPI)
- Use AWS Amplify or Google Cloud Run for Streamlit frontend
- Not recommended unless you need specific enterprise features

---

## Step-by-Step: Option 1 (Recommended)

### Prerequisites
- GitHub account with your code pushed
- Vercel account (free tier available)
- Streamlit account (free tier available)

### Backend Deployment on Vercel

**Step 1: Setup Vercel Config**

Create these files in your repo root:

**File: `vercel.json`**
```json
{
  "builds": [
    {
      "src": "backend/api/main.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "50mb" }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/api/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "backend/api/main.py"
    }
  ]
}
```

**File: `backend/api/index.py`** (rename or copy from main.py for Vercel)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Add CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Step 2: Deploy to Vercel**
```bash
npm install -g vercel
vercel login
vercel --prod
```

**Step 3: Get Your Backend URL**
After deployment, Vercel shows your URL (e.g., `https://blood-report-advanced.vercel.app`)

### Frontend Deployment on Streamlit Cloud

**Step 1: Push to GitHub**
```bash
git add .
git commit -m "Deploy Blood Report Analyzer"
git push origin main
```

**Step 2: Go to https://streamlit.io/cloud**

**Step 3: Click "New app"**
- GitHub repo: select your repo
- Branch: `main`
- File path: `frontend/app.py`

**Step 4: Configure Environment**
- Click "Advanced settings"
- Add secret: `api_url = https://blood-report-advanced.vercel.app`

**Step 5: Deploy!**

---

## Configuration for Production

### Update Frontend API URL

In `frontend/app.py`, the app already reads from environment:
```python
try:
    API_URL = st.secrets.get("api_url", "http://127.0.0.1:8000")
except:
    API_URL = "http://127.0.0.1:8000"
```

When deployed on Streamlit Cloud, add your backend URL in Streamlit Cloud secrets.

### Backend CORS Settings

Already configured in the backend for all origins, but in production you can restrict:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-streamlit-app.streamlit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Important Notes for Deployment

### Tesseract OCR
Tesseract is a system dependency. On Vercel/Streamlit Cloud:
- **Vercel**: Tesseract is not available in the default environment
  - **Solution**: Use AWS Textract or fallback to pytesseract without system install
  - **Alternative**: Deploy backend on AWS Lambda with Tesseract layer, or use a container service

- **Streamlit Cloud**: Tesseract is available in the default environment
  - No extra configuration needed for OCR to work

### PDF Handling
- PyPDF2 (installed) works server-side: ✅ Supported everywhere
- pdf2image requires Poppler: ⚠️ Not available on Vercel by default
  - **Solution**: Use PyPDF2 for text extraction (already primary method)

### File Size Limits
- Vercel: Max 50MB per function
- Streamlit Cloud: Reasonable for app files

---

## Troubleshooting

### Issue: "Tesseract not found" on Vercel

**Solutions:**
1. Use AWS Textract API (paid but reliable)
2. Deploy backend on Heroku/Render where system dependencies are easier to install
3. Add Tesseract as a custom layer (advanced)

### Issue: API connection timeout from Streamlit

**Solutions:**
1. Increase timeout in `frontend/app.py`:
```python
requests.post(f"{API_URL}/upload-report", files=files, timeout=120)
```

2. Check Vercel logs for backend errors:
```bash
vercel logs <project-name>
```

### Issue: Cold start delays (first request takes 10-30s)

This is normal on serverless platforms. Solutions:
- Upgrade to Vercel Pro for better performance
- Use a keep-alive service (e.g., UptimeRobot) to ping backend periodically
- Switch to Always-On services like Render or Railway

---

## Cost Estimates (Free Tier)

| Service | Free Tier | Limits |
|---------|-----------|--------|
| Vercel | ✅ Yes | 100 serverless function invocations/day, 1GB bandwidth |
| Streamlit Cloud | ✅ Yes | 1 app, 3 secrets, 1 GB/month storage |
| **Total** | ✅ Free | Suitable for low-traffic demo |

For production traffic:
- Vercel Pro: $20/month
- Streamlit Cloud Pro: $15/month (optional)

---

## Quick Deploy Checklist

- [ ] Push code to GitHub
- [ ] Create `vercel.json` in root
- [ ] Create `backend/api/index.py` (Vercel entry point)
- [ ] Test locally with `vercel dev`
- [ ] Deploy backend: `vercel --prod`
- [ ] Get backend URL
- [ ] Go to Streamlit Cloud
- [ ] Create new app, select GitHub repo
- [ ] Add API URL to Streamlit secrets
- [ ] Monitor logs and test

---

## Questions?

For help with:
- **Vercel**: https://vercel.com/docs
- **Streamlit Cloud**: https://docs.streamlit.io/streamlit-cloud
- **FastAPI**: https://fastapi.tiangolo.com
