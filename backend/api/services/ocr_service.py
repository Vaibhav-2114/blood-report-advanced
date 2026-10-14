import io
import logging
import os

import pytesseract
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

# Use the common Windows install path when present; otherwise use PATH.
WINDOWS_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(WINDOWS_TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = WINDOWS_TESSERACT_PATH

TESSERACT_CONFIG = "--oem 1 --psm 6"
MAX_IMAGE_WIDTH = 1600
MAX_PDF_PAGES = 3


def check_tesseract_installed() -> bool:
    """Return whether the Tesseract executable can be called."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except (pytesseract.TesseractNotFoundError, OSError):
        return False


def optimize_image(image: Image.Image, max_width: int = MAX_IMAGE_WIDTH) -> Image.Image:
    """Resize wide images to reduce OCR processing time."""
    if image.width <= max_width:
        return image
    ratio = max_width / image.width
    return image.resize(
        (max_width, max(1, int(image.height * ratio))),
        Image.Resampling.LANCZOS,
    )


def extract_text_from_pdf_pypdf2(pdf_bytes: bytes):
    """Extract embedded text from a PDF without requiring OCR tools."""
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for page_number, page in enumerate(reader.pages[:10], start=1):
            try:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    pages.append(f"--- Page {page_number} ---\n{page_text}")
            except Exception:
                logger.exception("Could not extract text from PDF page %s", page_number)
        return "\n\n".join(pages) or None
    except ImportError:
        logger.warning("PyPDF2 is not installed")
        return None
    except Exception:
        logger.exception("Could not read PDF text")
        return None


def convert_pdf_to_images(pdf_bytes: bytes):
    """Convert the first few scanned PDF pages to images; requires Poppler."""
    try:
        from pdf2image import convert_from_bytes

        return convert_from_bytes(
            pdf_bytes,
            first_page=1,
            last_page=MAX_PDF_PAGES,
            dpi=150,
        )
    except ImportError:
        logger.warning("pdf2image is not installed")
        return None
    except Exception:
        logger.exception("Could not convert PDF pages to images (Poppler may be missing)")
        return None


def _run_ocr(image: Image.Image) -> str:
    if not check_tesseract_installed():
        raise RuntimeError(
            "Tesseract OCR is not installed or is not on PATH. "
            "Install Tesseract to process image reports or scanned PDFs."
        )
    return pytesseract.image_to_string(optimize_image(image.convert("RGB")), config=TESSERACT_CONFIG).strip()


def image_to_text(file_bytes: bytes) -> str:
    """Extract text from a text PDF, scanned PDF, or supported image."""
    if not file_bytes:
        return "Error: Uploaded file is empty."

    try:
        if file_bytes.startswith(b"%PDF"):
            logger.info("Processing PDF upload")

            # Text-based PDFs do not need Tesseract or Poppler.
            embedded_text = extract_text_from_pdf_pypdf2(file_bytes)
            if embedded_text:
                return embedded_text

            images = convert_pdf_to_images(file_bytes)
            if images is None:
                return (
                    "Error: This PDF has no extractable text. Scanned-PDF OCR needs "
                    "Tesseract and Poppler installed on the backend."
                )
            if not images:
                return "Error: No pages could be read from the PDF."

            page_text = []
            for page_number, image in enumerate(images, start=1):
                try:
                    text = _run_ocr(image)
                    if text:
                        page_text.append(f"--- Page {page_number} ---\n{text}")
                except RuntimeError as error:
                    return f"Error: {error}"
                except Exception:
                    logger.exception("OCR failed for PDF page %s", page_number)
            return "\n\n".join(page_text) or "No text detected in scanned PDF."

        try:
            with Image.open(io.BytesIO(file_bytes)) as image:
                image.load()
                text = _run_ocr(image)
        except (UnidentifiedImageError, OSError):
            return "Error: Unsupported or invalid image file."

        return text or "No text detected in image."
    except RuntimeError as error:
        return f"Error: {error}"
    except Exception:
        logger.exception("Unexpected report text extraction error")
        return "Error: Could not process this report. Check the file and server logs."
