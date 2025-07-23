# utils/pdf_processor.py
import pdfplumber

# NOTE: We are removing OCR from the primary flow for now to focus on the chunking problem.
# Digital extraction is much more reliable for financial reports.

def extract_pages_from_pdf(pdf_path):
    """
    Extracts text from a PDF file, returning a list where each item is the text of one page.
    """
    page_texts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    page_texts.append(text)
        
        if not page_texts:
            print("Warning: pdfplumber extracted no pages with text.")
            return None
        
        return page_texts
    except Exception as e:
        print(f"Error reading PDF with pdfplumber: {e}")
        # Here you could add the OCR fallback if needed, but it's often less reliable for tables.
        return None