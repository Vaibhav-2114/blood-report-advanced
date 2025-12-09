# Copy-Paste Deployment Commands

## Phase 1: Prepare Code (Local)

### Step 1A: Add Files to Git
```bash
cd d:\blood-report-advanced
git add .
git commit -m "Prepare for deployment: add Vercel config and deployment guides"
git push origin main
```

### Step 1B: Verify Local Works (Optional but Recommended)
```bash
# Terminal 1 - Backend
venv\Scripts\activate
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 - Frontend (in another terminal)
venv\Scripts\activate
streamlit run frontend/app.py
```
Then test at http://localhost:8501

---

## Phase 2: Deploy Backend to Vercel

### Step 2A: Install Vercel CLI (One-time)
```bash
npm install -g vercel
```

### Step 2B: Login to Vercel
```bash
vercel login
```
This opens a browser to verify your account.

### Step 2C: Deploy to Vercel
```bash
cd d:\blood-report-advanced
vercel --prod
```

**OUTPUT:** Vercel will show your deployment URL
```
✅ Production: https://blood-report-advanced.vercel.app
```

**IMPORTANT:** Copy this URL and save it! You'll need it for the frontend.

---

## Phase 3: Deploy Frontend to Streamlit Cloud

### Step 3A: Ensure GitHub Has Latest Code
```bash
cd d:\blood-report-advanced
git status
# If changes, commit and push:
git add .
git commit -m "Final deployment setup"
git push origin main
```

### Step 3B: Open Streamlit Cloud & Create App
1. Go to: https://streamlit.io/cloud
2. Click "New app"
3. Fill in:
   - **GitHub repo:** your-username/blood-report-advanced
   - **Branch:** main
   - **Main file path:** frontend/app.py
4. Click "Deploy"

### Step 3C: Add Environment Variables (IMPORTANT!)
1. In Streamlit Cloud app page, click "Settings" (gear icon)
2. Click "Secrets"
3. Add this exactly:
```
api_url = "https://blood-report-advanced.vercel.app"
```
(Replace with your actual Vercel URL from Phase 2)

4. Save

**NOTE:** Streamlit will automatically restart your app

---

## Phase 4: Verify Deployment

### Test Backend API
```bash
# Test in browser or PowerShell
Invoke-WebRequest -Uri "https://blood-report-advanced.vercel.app/docs" -UseBasicParsing
```
Should show FastAPI documentation page.

### Test Frontend App
1. Go to your Streamlit Cloud app URL (shown in dashboard)
2. You should see the Blood Report Analyzer interface
3. Try uploading a test blood report image

### Full End-to-End Test
1. Open Streamlit app
2. Upload blood report
3. Click "Analyze"
4. Verify results appear in tabs

---

## Phase 5: Monitor & Debug (If Issues)

### Check Vercel Backend Logs
```bash
# Install Vercel CLI if not done
npm install -g vercel

# View logs
vercel logs blood-report-advanced
```

### Check Streamlit Frontend Logs
1. Go to Streamlit Cloud dashboard
2. Click your app
3. Click "Settings" → "Logs"
4. View output/errors

### Common Issues & Fixes

**Issue: "Cannot connect to API"**
```
Fix: Check Streamlit secrets - api_url must match Vercel deployment URL exactly
```

**Issue: "Tesseract not found"**
```
Expected on Vercel. OCR will fail, but PyPDF2 text extraction should work.
```

**Issue: Timeout errors**
```
Fix: Increase timeout in frontend/app.py:
- Change timeout=60 to timeout=120
- Change timeout=30 to timeout=60
- Redeploy
```

---

## Phase 6: Future Updates

### Update Backend Only
```bash
# Make changes to backend code
cd d:\blood-report-advanced

# Test locally first
venv\Scripts\activate
python -m uvicorn backend.api.main:app --reload

# Commit and deploy
git add .
git commit -m "Update backend: [description]"
git push origin main
vercel --prod
```

### Update Frontend Only
```bash
# Make changes to frontend/app.py
cd d:\blood-report-advanced

# Test locally first
venv\Scripts\activate
streamlit run frontend/app.py

# Commit and auto-deploys
git add .
git commit -m "Update frontend: [description]"
git push origin main
```
Streamlit Cloud auto-redeploys on git push.

### Update Both
```bash
# Make changes to both backend and frontend

# Test locally
start-local.bat

# Commit and deploy
git add .
git commit -m "Update: [description]"
git push origin main
vercel --prod  # For backend
# Frontend auto-redeploys
```

---

## PowerShell Aliases (Optional)

Add to your PowerShell profile to simplify:

```powershell
# Open PowerShell profile
notepad $PROFILE

# Add these lines:
function Deploy-Backend { vercel --prod }
function Deploy-Frontend { git push origin main }
function Start-Local { & ".\start-local.bat" }
function Test-Backend { Invoke-WebRequest "https://blood-report-advanced.vercel.app/docs" }

# Save and restart PowerShell
```

Then use:
```bash
Deploy-Backend    # Deploy to Vercel
Deploy-Frontend   # Push to GitHub (auto-deploys Streamlit)
Start-Local       # Run locally
Test-Backend      # Check if backend is up
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Run locally | `start-local.bat` |
| Deploy backend | `vercel --prod` |
| Deploy frontend | `git push origin main` |
| View backend logs | `vercel logs blood-report-advanced` |
| View frontend logs | Streamlit Cloud dashboard → Settings → Logs |
| Test backend API | https://blood-report-advanced.vercel.app/docs |
| Update Streamlit secrets | Streamlit Cloud → Settings → Secrets |

---

## URLs (After Deployment)

Save these after deploying:

```
Backend API:     https://blood-report-advanced.vercel.app
API Docs:        https://blood-report-advanced.vercel.app/docs
Frontend:        https://blood-report-analyzer-[username].streamlit.app
```

---

## Support

- **Vercel Issues**: https://vercel.com/help
- **Streamlit Issues**: https://discuss.streamlit.io
- **FastAPI Issues**: https://github.com/tiangolo/fastapi/discussions

Good luck with your deployment! 🚀
