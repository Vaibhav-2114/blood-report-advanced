from PIL import Image
import io
import pytesseract
import os
import logging

logger = logging.getLogger(__name__)

# Configure Tesseract path for Windows
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.pytesseract_cmd = TESSERACT_PATH

# Optimize Tesseract config for faster processing
TESSERACT_CONFIG = r'--oem 1 --psm 6'

def check_tesseract_installed():
    """Check if Tesseract is installed and accessible."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except pytesseract.TesseractNotFoundError:
        return False

def optimize_image(img, max_width=1024):
    """Optimize image size for faster OCR processing."""
    # Resize if too large
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    return img

def extract_text_from_pdf_pypdf2(pdf_bytes: bytes):
    """Extract text directly from PDF using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text = []
        
        # Extract text from all pages (max 10 pages to avoid timeout)
        num_pages = min(len(reader.pages), 10)
        for page_num in range(num_pages):
            try:
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text.strip():
                    text.append(f"--- Page {page_num + 1} ---\n{page_text}")
            except Exception as e:
                logger.error(f"Error extracting text from page {page_num + 1}: {str(e)}")
        
        return "\n\n".join(text) if text else None
    except ImportError:
        logger.warning("PyPDF2 not installed")
        return None
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        return None

def convert_pdf_to_images(pdf_bytes: bytes):
    """Convert PDF pages to images using pdf2image."""
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=3, dpi=150)  # Convert first 3 pages max, lower DPI for speed
        return images
    except ImportError:
        logger.warning("pdf2image library not installed")
        return None
    except Exception as e:
        logger.error(f"Error converting PDF: {str(e)}")
        return None

def image_to_text(image_bytes: bytes) -> str:
    try:
        if not image_bytes or len(image_bytes) == 0:
            return "Error: Empty file"
        
        # Check if Tesseract is installed
        if not check_tesseract_installed():
            return "Error: Tesseract OCR is not installed. Please install it from: https://github.com/UB-Mannheim/tesseract/wiki or run: winget install UB-Mannheim.TesseractOCR"
        
        # Check if it's a PDF file
        is_pdf = image_bytes[:4] == b'%PDF'
        
        if is_pdf:
            logger.info("Processing PDF file")
            
            # Try PyPDF2 first (direct text extraction, faster)
            text = extract_text_from_pdf_pypdf2(image_bytes)
            if text:
                logger.info(f"Extracted text from PDF using PyPDF2: {len(text)} characters")
                return text
            
            # Fallback: Try converting PDF to images and use OCR
            logger.info("PyPDF2 extraction returned no text, attempting image conversion")
            images = convert_pdf_to_images(image_bytes)
            
            if images is None:
                return "Error: Could not process PDF. pdf2image requires poppler to be installed. Please install poppler from https://github.com/oschwartz10612/poppler-windows/releases/"
            
            if not images:
                return "Error: Could not extract pages from PDF"
            
            # Process all extracted images with OCR
            all_text = []
            for page_num, img in enumerate(images, 1):
                try:
                    img = img.convert("RGB")
                    img = optimize_image(img)
                    logger.info(f"Processing PDF page {page_num} with OCR, size: {img.size}")
                    ocr_text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
                    if ocr_text.strip():
                        all_text.append(f"--- Page {page_num} ---\n{ocr_text}")
                except Exception as e:
                    logger.error(f"Error processing PDF page {page_num}: {str(e)}")
                    all_text.append(f"--- Page {page_num} (Error) ---\nFailed to process page: {str(e)}")
            
            return "\n\n".join(all_text) if all_text else "No text detected in PDF"
        
        else:
            # Process as regular image
            logger.info("Processing image file")
            byte_stream = io.BytesIO(image_bytes)
            try:
                img = Image.open(byte_stream)
                img.verify()  # Verify it's a valid image
                
                # Re-open since verify() closes the file
                byte_stream.seek(0)
                img = Image.open(byte_stream).convert("RGB")
                
                # Optimize image for faster processing
                img = optimize_image(img)
            except (IOError, Image.UnidentifiedImageError) as img_err:
                return f"Error: Invalid image format - {str(img_err)}"
            
            logger.info(f"Processing image of size {img.size}")
            text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
            return text if text.strip() else "No text detected in image"
    
    except pytesseract.TesseractNotFoundError:
        return "Error: Tesseract is not installed or not in PATH. Install from: https://github.com/UB-Mannheim/tesseract/wiki"
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return f"Error processing file: {str(e)}"




