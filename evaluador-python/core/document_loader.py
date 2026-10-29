"""Entrada de documentos: validación, detección de formato y carga."""
from pathlib import Path

from .pdf_extractor import extract_pdf_pages, ocr_image
from .word_extractor import extract_docx_all

ALLOWED_EXT = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def detect_format(file_path):
    return Path(file_path).suffix.lower()


def validate_file(file_path):
    ext = detect_format(file_path)
    if ext not in ALLOWED_EXT:
        raise ValueError(f"Formato no soportado: {ext}. Usa PDF, Word o imagen.")
    if not Path(file_path).exists():
        raise FileNotFoundError(f"No existe el archivo: {file_path}")
    return ext


def load_document(file_path):
    ext = validate_file(file_path)
    if ext == ".pdf":
        pages = extract_pdf_pages(file_path)
        texto = "\n".join(p["texto"] for p in pages)
        return {"formato": "pdf", "texto": texto, "paginas": pages}
    if ext == ".docx":
        texto = extract_docx_all(file_path)
        return {"formato": "docx", "texto": texto, "paginas": []}
    if ext == ".doc":
        raise ValueError("El formato .doc no está soportado; guarda el archivo como .docx")
    if ext in IMAGE_EXT:
        texto = ocr_image(file_path)
        return {"formato": "imagen", "texto": texto, "paginas": []}
    raise ValueError(f"Formato no soportado: {ext}")
