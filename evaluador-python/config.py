"""Configuración general del evaluador documental."""
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = DATA_DIR / "temp"
TESSDATA_DIR = DATA_DIR / "tessdata"
CHECKLIST_PATH = BASE_DIR / "rules" / "checklist.yaml"
REPORTS_DIR = BASE_DIR / "reports" / "output"

# OCR
TESSERACT_CMD = os.getenv(
    "TESSERACT_CMD",
    shutil.which("tesseract") or r"C:\Program Files\Tesseract-OCR\tesseract.exe",
)
OCR_LANG = "spa"
OCR_DPI = 300
OCR_MIN_CHARS = 40  # si una página tiene menos texto, se hace OCR

# IA opcional
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

for d in (DATA_DIR, TEMP_DIR, TESSDATA_DIR, REPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Tesseract debe encontrar los .traineddata (spa, eng, osd)
os.environ.setdefault("TESSDATA_PREFIX", str(TESSDATA_DIR))
