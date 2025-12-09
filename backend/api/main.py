from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from .services import ocr_service, extract_service, ml_service
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blood Report Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-report")
async def upload_report(file: UploadFile = File(...)):
    try:
        logger.info(f"Processing file: {file.filename}")
        content = await file.read()
        logger.info(f"File size: {len(content)} bytes")
        text = ocr_service.image_to_text(content)
        logger.info(f"OCR extraction complete, text length: {len(text)}")
        values = extract_service.extract_key_values(text)
        logger.info(f"Extracted {len(values)} parameters")
        return JSONResponse({"text": text, "values": values})
    except Exception as e:
        logger.error(f"Error in upload_report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze(values: dict):
    try:
        if not isinstance(values, dict):
            raise HTTPException(status_code=400, detail="values must be a dict")
        logger.info(f"Analyzing {len(values)} values")
        comparison = ml_service.compare_with_ranges(values)
        prediction = ml_service.predict_risk(values)
        logger.info(f"Analysis complete: {prediction}")
        return JSONResponse({"comparison": comparison, "prediction": prediction})
    except Exception as e:
        logger.error(f"Error in analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status":"ok", "message": "Blood Report Analyzer Backend"}

if __name__ == "__main__":
    uvicorn.run("backend.api.main:app", host="127.0.0.1", port=8000, reload=True)
