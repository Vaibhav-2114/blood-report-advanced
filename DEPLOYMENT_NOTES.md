# Deployment Configuration

## Files Created for Deployment

### 1. **vercel.json**
Configures how Vercel builds and deploys the FastAPI backend.

### 2. **backend/api/index.py**
Vercel entry point for the FastAPI application. Required for Vercel routing.

### 3. **.streamlit/config.toml**
Streamlit configuration for theme and server settings.

### 4. **.streamlit/secrets.toml**
Local development secrets. For production, use Streamlit Cloud dashboard.

---

## Recommended Deployment Path

### Step 1: Deploy Backend to Vercel (5 minutes)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd d:\blood-report-advanced
vercel --prod
```

Save the URL: `https://your-project-name.vercel.app`

### Step 2: Deploy Frontend to Streamlit Cloud (10 minutes)

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Click "New app"
4. Select your repository and `frontend/app.py`
5. In Advanced settings, add:
   ```
   api_url = https://your-project-name.vercel.app
   ```
6. Deploy!

### Step 3: Test Live Deployment

- Open Streamlit Cloud app URL
- Upload a test blood report
- Verify analysis works end-to-end

---

## Important Caveats for Vercel

### ⚠️ Tesseract OCR
Tesseract requires system dependencies not available on Vercel's free tier.

**Solutions:**
1. **Use AWS Textract** (recommended)
   - More reliable and scalable
   - Requires AWS account and API key
   - Cost: $1.50 per 1000 pages

2. **Move backend to Render.com or Railway.app**
   - System dependencies are available
   - Similar to Vercel, with better OS support
   - Free tier available

3. **Disable OCR on Vercel, keep on Streamlit Cloud**
   - Frontend runs on Streamlit Cloud (has Tesseract)
   - Only backend runs on Vercel (just for disease prediction)
   - Requires refactoring code

### ⚠️ File Upload Size
- Vercel free: Limited to ~50MB per function
- Streamlit Cloud: Reasonable limits
- Solution: Compress images before upload, or use chunked uploads

---

## Alternative: Deploy Everything on Render.com

If Vercel's limitations are problematic:

### Backend on Render
```
Service: Web Service
Repository: Your GitHub repo
Build Command: pip install -r backend/requirements.txt
Start Command: uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
Environment: Add PYTHONUNBUFFERED=true
```

### Frontend on Streamlit Cloud
(Same as above)

**Advantages:**
- Tesseract works out of the box
- Better for long-running tasks
- More generous free tier

**Cost:** Free tier available, paid tier ~$10/month per service

---

## Monitoring & Logs

### Vercel Backend Logs
```bash
vercel logs <project-name>
```

### Streamlit Cloud Logs
- View directly in Streamlit Cloud dashboard under "Settings" → "Logs"

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "Module not found" | Missing dependencies | Ensure all in requirements.txt |
| "Tesseract not found" | System dependency missing | Use AWS Textract or Render |
| Timeout errors | Long processing | Increase timeout, optimize images |
| CORS errors | API URL mismatch | Check Streamlit secrets match deployed URL |
| Cold start delays | Serverless initialization | Use keep-alive service or pro tier |

---

## Cost Breakdown

| Component | Service | Free Tier | Cost (Monthly) |
|-----------|---------|-----------|----------------|
| Backend API | Vercel | Yes | $0 (generous free tier) |
| Frontend App | Streamlit Cloud | Yes | $0 |
| Domain | (optional) | - | $10-15/year |
| **Total** | | | **$0-2/month** |

For production traffic (>100K requests/month):
- Vercel Pro: $20/month
- Streamlit Cloud Pro: $15/month (optional)
- AWS Textract: ~$50-100/month (if using OCR heavily)

---

## Security Best Practices

### For Production

1. **Backend API Security**
   ```python
   # In backend/api/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-streamlit-app.streamlit.app"],  # Restrict origin
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Input Validation**
   - Already implemented in backend
   - Validates file size, type, and content

3. **Rate Limiting** (Optional)
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

4. **Environment Variables**
   - Never commit `.env` files
   - Use Vercel/Streamlit secrets for sensitive data
   - Example: API keys, database URLs

---

## Next Steps After Deployment

1. **Monitor Performance**
   - Check Vercel/Streamlit logs regularly
   - Set up error tracking (Sentry, LogRocket)

2. **Gather User Feedback**
   - Add feedback form to app
   - Track common errors and feature requests

3. **Optimize**
   - Profile slow endpoints
   - Cache results if applicable
   - Optimize image processing

4. **Scale**
   - Plan for higher traffic
   - Consider database for result history
   - Implement user authentication if needed

---

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-cloud
- **FastAPI Docs**: https://fastapi.tiangolo.com/deployment/
- **Render Docs**: https://render.com/docs

Good luck with your deployment! 🚀
