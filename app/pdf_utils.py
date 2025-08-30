import fitz 
from pdfminer.high_level import extract_text as extract_text_pdfminer
from pdf2image import convert_from_path
import pytesseract

def extract_text_fitz(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        return "\n".join([page.get_text() for page in doc])
    except Exception as e:
        return e

def extract_text_pdfminer_safe(pdf_path):
    try:
        return extract_text_pdfminer(pdf_path)
    except Exception as e:
        return e

def extract_text_ocr(pdf_path, lang='vie'):
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        text_list = []
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page, lang=lang)
            text_list.append(text)
        return "\n".join(text_list)
    except Exception as e:
        return e

def robust_pdf_to_text(pdf_path):
    # text = extract_text_fitz(pdf_path)
    # if len(text.strip()) >= 500:
    #     return text

    # text = extract_text_pdfminer_safe(pdf_path)
    # if len(text.strip()) >= 500:
    #     return text

    text = extract_text_ocr(pdf_path)
    return text