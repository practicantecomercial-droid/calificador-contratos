"""Lectura de documentos para el motor de reconocimiento.

Extrae texto por pÃ¡gina y, sobre todo, los campos clave-valor que usan los
contratos del ERP (etiqueta en una lÃ­nea, valor en la siguiente). No importa
``pytesseract`` al cargar el mÃ³dulo: el OCR es opcional y perezoso, de modo que
la lectura de PDF/Word con texto no depende de esa cadena.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

OCR_MIN_CHARS = 40
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}

_MAX_LINEAS_VALOR = 8
_MAX_CHARS_VALOR = 500

_RE_ETIQUETA = re.compile(r"^(?P<etiqueta>[^:]{1,60}):\s*(?P<valor>.*)$")
_RE_HORA = re.compile(r"^\d{1,2}$")

_SECCIONES_CORTE = {
    "cantidades de obra", "contrato detallado por grupos",
    "vo bo", "elaborado por", "pre aprobado por",
    "aprobado por", "item", "valor total", "contratante", "contratista",
}

_ETIQUETAS_CABECERA = {"empresa", "nit", "direccion", "telefono", "ciudad"}

# Campos conocidos del ERP. Evita que una frase del valor (p. ej.
# "BUEN MANEJO DE ANTICIPO: ...") se interprete como una etiqueta nueva.
ETIQUETAS_ERP = {
    "empresa", "nit", "direccion", "telefono", "ciudad",
    "fecha y hora de impresion", "contratista", "nit/cc", "email",
    "proyecto", "tipo contrato", "valor contrato", "estado",
    "otrosi contrato", "fecha inicio", "fecha terminacion",
    "forma de pago", "referencia", "administracion", "imprevistos",
    "utilidad", "ret garantias", "iva", "ret anticipo", "ret fic",
    "descripcion", "observaciones",
}


def _sin_tildes(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def _limpiar_linea(texto: str) -> str:
    return re.sub(r"[ \t]+", " ", texto.replace("\xa0", " ")).strip()


def normalizar_clave(texto: str) -> str:
    """Clave estable para buscar campos (sin tildes, % ni puntuaciÃ³n)."""
    clave = _sin_tildes(texto.lower()).replace("%", " ")
    clave = re.sub(r"[.:;]+", " ", clave)
    return re.sub(r"\s+", " ", clave).strip()


def es_corte(texto: str) -> bool:
    return normalizar_clave(texto) in _SECCIONES_CORTE


def es_etiqueta_valida(linea: str):
    match = _RE_ETIQUETA.match(linea)
    if not match:
        return None
    etiqueta = match.group("etiqueta").strip()
    if not etiqueta or "http" in etiqueta.lower() or _RE_HORA.fullmatch(etiqueta):
        return None
    if re.search(r"\d", etiqueta) and re.search(r"[/.,]", etiqueta):
        return None

    clave = normalizar_clave(etiqueta)
    if clave in ETIQUETAS_ERP:
        return match
    # Etiquetas genéricas: solo si no traen valor en la misma línea.
    if not match.group("valor").strip() and len(etiqueta) <= 40:
        return match
    return None


def _leer_pdf(path: Path):
    import pymupdf

    paginas = []
    with pymupdf.open(path) as doc:
        for numero, page in enumerate(doc, start=1):
            texto = (page.get_text("text") or "").strip()
            ocr = False
            error = None
            if len(texto) < OCR_MIN_CHARS:
                try:
                    texto = _ocr_pagina(page)
                    ocr = True
                except Exception as exc:  # OCR opcional
                    error = str(exc)
            pagina = {
                "pagina": numero,
                "texto": texto,
                "caracteres": len(texto),
                "ocr": ocr,
            }
            if error:
                pagina["ocr_error"] = error
            paginas.append(pagina)
    return paginas


def _ocr_pagina(page):
    import pytesseract
    from PIL import Image

    try:
        import config

        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
        lang = config.OCR_LANG
        dpi = config.OCR_DPI
    except Exception:
        lang, dpi = "spa", 300

    pix = page.get_pixmap(dpi=dpi)
    imagen = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return pytesseract.image_to_string(imagen, lang=lang).strip()


def _leer_docx(path: Path):
    from docx import Document

    doc = Document(path)
    partes = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            partes.append(" | ".join(cell.text for cell in row.cells))
    texto = "\n".join(partes)
    return [{"pagina": 1, "texto": texto, "caracteres": len(texto), "ocr": False}]


def _leer_imagen(path: Path):
    import pytesseract
    from PIL import Image

    try:
        import config

        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
        lang = config.OCR_LANG
    except Exception:
        lang = "spa"

    texto = pytesseract.image_to_string(Image.open(path).convert("RGB"), lang=lang).strip()
    return [{"pagina": 1, "texto": texto, "caracteres": len(texto), "ocr": True}]


def _construir_lineas(paginas):
    lineas = []
    numero = 0
    for pagina in paginas:
        for cruda in (pagina.get("texto") or "").splitlines():
            numero += 1
            lineas.append({
                "n": numero,
                "texto": _limpiar_linea(cruda),
                "pagina": pagina.get("pagina"),
            })
    return lineas


def _detectar_bloques(lineas):
    """Detecta cabeceras tabulares: N etiquetas seguidas de N valores."""
    bloques = []
    i = 0
    while i < len(lineas):
        texto = lineas[i]["texto"]
        if es_etiqueta_valida(texto):
            i += 1
            continue
        if normalizar_clave(texto) not in _ETIQUETAS_CABECERA:
            i += 1
            continue

        etiquetas = []
        j = i
        while (
            j < len(lineas)
            and normalizar_clave(lineas[j]["texto"]) in _ETIQUETAS_CABECERA
            and not es_etiqueta_valida(lineas[j]["texto"])
        ):
            etiquetas.append(lineas[j]["texto"])
            j += 1

        valores = []
        k = j
        while k < len(lineas) and len(valores) < len(etiquetas):
            actual = lineas[k]["texto"]
            if not actual or es_etiqueta_valida(actual) or es_corte(actual):
                break
            valores.append(actual)
            k += 1

        if len(valores) == len(etiquetas):
            bloques.append({
                "tipo": "cabecera",
                "pagina": lineas[i]["pagina"],
                "etiquetas": etiquetas,
                "valores": valores,
                "campos": {
                    normalizar_clave(etiqueta): valor
                    for etiqueta, valor in zip(etiquetas, valores)
                },
            })
            i = k
            continue
        i += 1
    return bloques


def _extraer_campos(lineas):
    campos = {}
    lista = []
    i = 0
    while i < len(lineas):
        match = es_etiqueta_valida(lineas[i]["texto"])
        if not match:
            i += 1
            continue

        etiqueta = match.group("etiqueta").strip()
        inline = match.group("valor").strip()
        j = i + 1
        valor_lineas = []
        if inline:
            valor = inline
        else:
            while j < len(lineas) and len(valor_lineas) < _MAX_LINEAS_VALOR:
                actual = lineas[j]["texto"]
                if not actual or es_etiqueta_valida(actual) or es_corte(actual):
                    break
                valor_lineas.append(actual)
                j += 1
                if len(" ".join(valor_lineas)) >= _MAX_CHARS_VALOR:
                    break
            valor = " ".join(valor_lineas).strip()

        campo = {
            "clave": normalizar_clave(etiqueta),
            "etiqueta": etiqueta,
            "valor": valor,
            "vacio": not valor,
            "pagina": lineas[i]["pagina"],
            "linea": lineas[i]["n"],
            "lineas": [lineas[i]["n"]] + [lineas[k]["n"] for k in range(i + 1, j)],
        }
        lista.append(campo)
        if campo["clave"] in campos:
            campos[campo["clave"]].setdefault("duplicados", []).append(campo)
        else:
            campos[campo["clave"]] = campo

        i = j if not inline else i + 1
    return campos, lista


def _construir_documento(ruta, formato, texto, paginas):
    lineas = _construir_lineas(paginas)
    campos, campos_lista = _extraer_campos(lineas)
    return {
        "ruta": str(ruta),
        "formato": formato,
        "texto": texto,
        "paginas": paginas,
        "lineas": lineas,
        "campos": campos,
        "campos_lista": campos_lista,
        "campos_vacios": [c["clave"] for c in campos_lista if c["vacio"]],
        "bloques": _detectar_bloques(lineas),
    }


def leer_texto(texto, nombre="texto", formato="texto"):
    """Construye la estructura de documento a partir de texto plano (pruebas)."""
    paginas = [{"pagina": 1, "texto": texto, "caracteres": len(texto), "ocr": False}]
    return _construir_documento(nombre, formato, texto, paginas)


def leer_documento(ruta):
    path = Path(ruta)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    ext = path.suffix.lower()
    if ext == ".pdf":
        paginas = _leer_pdf(path)
    elif ext == ".docx":
        paginas = _leer_docx(path)
    elif ext in IMAGE_EXT:
        paginas = _leer_imagen(path)
    elif ext == ".doc":
        raise ValueError("El formato .doc no estÃ¡ soportado; guarda el archivo como .docx")
    else:
        raise ValueError(f"Formato no soportado: {ext}. Usa PDF, Word o imagen.")

    texto = "\n".join(p.get("texto", "") for p in paginas)
    return _construir_documento(ruta, ext.lstrip("."), texto, paginas)


def campo(documento, *claves):
    """Devuelve el primer campo cuya clave coincida exactamente o por fragmentos."""
    campos = documento.get("campos", {})
    for clave in claves:
        if clave in campos:
            return campos[clave]
    for nombre, valor in campos.items():
        if all(fragmento in nombre for fragmento in claves):
            return valor
    return None
