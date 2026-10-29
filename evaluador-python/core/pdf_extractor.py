"""Extracción de texto de PDF, con OCR para páginas escaneadas."""
import pytesseract
from PIL import Image

import config

try:
    import pymupdf
except ImportError:  # pragma: no cover
    import fitz as pymupdf

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD


def _ocr_pixmap(pix):
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return pytesseract.image_to_string(img, lang=config.OCR_LANG)


def extract_pdf_pages(file_path, min_chars=None):
    """Devuelve [{pagina, texto, caracteres, ocr}] por página."""
    umbral = config.OCR_MIN_CHARS if min_chars is None else min_chars
    pages = []
    with pymupdf.open(file_path) as doc:
        for i, page in enumerate(doc, start=1):
            text = (page.get_text("text") or "").strip()
            used_ocr = False
            if len(text) < umbral:
                try:
                    pix = page.get_pixmap(dpi=config.OCR_DPI)
                    text = _ocr_pixmap(pix).strip()
                    used_ocr = True
                except Exception:
                    used_ocr = False
            pages.append({
                "pagina": i,
                "texto": text,
                "caracteres": len(text),
                "ocr": used_ocr,
            })
    return pages


def extract_pdf_text(file_path):
    return "\n".join(p["texto"] for p in extract_pdf_pages(file_path))


def ocr_image(file_path):
    img = Image.open(file_path).convert("RGB")
    return pytesseract.image_to_string(img, lang=config.OCR_LANG)
