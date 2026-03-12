import pytesseract
from pdf2image import convert_from_path
import PyPDF2
import os
import nltk

# Ensure NLTK data is ready
try:
    nltk.download('punkt', quiet=True)
except Exception:
    pass

class OCRService:
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """Extracts text from PDF, uses PyPDF2 first, falls back to OCR."""
        text = ""
        try:
            # 1. Try PyPDF2 for text-based PDFs (Fast)
            print(f"OCRService: Trying PyPDF2 for {pdf_path}")
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                print(f"OCRService: PDF has {num_pages} pages.")
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # 2. If very little text was extracted, it might be an image-based or poorly formatted PDF
            if not text.strip() or len(text.strip()) < 100:
                print(f"OCRService: Insufficient text ({len(text)}) found via PyPDF2, falling back to Tesseract OCR...")
                try:
                    pages = convert_from_path(pdf_path)
                    print(f"OCRService: Converted PDF to {len(pages)} images.")
                    for i, page in enumerate(pages):
                        print(f"OCRService: OCRing page {i+1}...")
                        text += pytesseract.image_to_string(page) + "\n"
                except Exception as ocr_err:
                    print(f"OCRService: Tesseract/Poppler failed: {ocr_err}")
            
            print(f"OCRService: Final extracted text length: {len(text)}")
            return text
        except Exception as e:
            print(f"OCRService Critical Extraction Error: {e}")
            return None

    @staticmethod
    def extract_text_from_image(image_path):
        try:
            return pytesseract.image_to_string(image_path)
        except Exception as e:
            print(f"OCR Error: {e}")
            return None
