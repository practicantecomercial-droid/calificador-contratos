"""Descarga los modelos de idioma de Tesseract necesarios para el OCR."""
import urllib.request
from pathlib import Path

BASE = "https://github.com/tesseract-ocr/tessdata/raw/main"
DEST = Path(__file__).resolve().parent.parent / "data" / "tessdata"
FILES = ["spa.traineddata", "eng.traineddata", "osd.traineddata"]


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        out = DEST / f
        if out.exists():
            print(f"{f}: ya existe")
            continue
        print(f"Descargando {f} ...")
        urllib.request.urlretrieve(f"{BASE}/{f}", str(out))
        print(f"{f}: listo")
    print(f"Modelos en: {DEST}")


if __name__ == "__main__":
    main()
