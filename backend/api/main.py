import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .services import extract_service, ml_service, ocr_service
from .services.disease_service import predict_diseases

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Blood Report Analyzer API",
    description="Educational demo API for extracting and comparing blood-test values.",
    version="1.0.0",
)

# The frontend and API are commonly deployed separately. Restrict CORS using
# BLOOD_REPORT_ALLOWED_ORIGINS in production; local development can use localhost.
import os

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "BLOOD_REPORT_ALLOWED_ORIGINS",
        "http://localhost:8501,http://127.0.0.1:8501",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Blood Report Analyzer Backend",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload-report")
async def upload_report(file: UploadFile = File(...)):
    filename = file.filename or "uploaded-file"
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File exceeds the 50 MB limit.")

        logger.info("Processing upload %r (%d bytes)", filename, len(content))
        text = ocr_service.image_to_text(content)
        values = extract_service.extract_key_values(text)
        logger.info("Extraction finished; %d parameters detected", len(values))
        return {"text": text, "values": values}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to process upload %r", filename)
        raise HTTPException(status_code=500, detail="Could not process the uploaded report.")
    finally:
        await file.close()


@app.post("/analyze")
async def analyze(values: dict):
    if not values:
        raise HTTPException(
            status_code=400,
            detail="No parameters were supplied. Check the extracted values and try again.",
        )

    numeric_values = {}
    for key, value in values.items():
        try:
            numeric_values[str(key)] = float(value)
        except (TypeError, ValueError):
            continue

    if not numeric_values:
        raise HTTPException(status_code=400, detail="No numeric parameters were supplied.")

    try:
        comparison = ml_service.compare_with_ranges(numeric_values)
        prediction = ml_service.predict_risk(numeric_values)
        diseases = predict_diseases(numeric_values)
        return {
            "comparison": comparison,
            "prediction": prediction,
            "diseases": diseases,
        }
    except Exception:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail="Could not analyze the supplied values.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api.main:app", host="127.0.0.1", port=8000, reload=True)
