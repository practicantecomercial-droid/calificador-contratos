"""Contexto contractual extraído de los campos del documento.

No decide cumplimiento: solo describe el contrato (tipo, partes, valor, fechas,
porcentajes, retenciones y pólizas mencionadas) para que la validación posterior
interprete cada requisito en su contexto correcto.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date

from .document_reader import campo

PORCENTAJES = {
    "administracion": ("administracion",),
    "imprevistos": ("imprevistos",),
    "utilidad": ("utilidad",),
    "ret_garantias": ("ret garantias",),
    "iva": ("iva",),
    "ret_anticipo": ("ret anticipo",),
    "ret_fic": ("ret fic",),
}

POLIZAS = {
    "buen_manejo_anticipo": ("buen manejo", "manejo de anticipo"),
    "cumplimiento": ("cumplimiento",),
    "calidad": ("calidad",),
    "salarios": ("salarios", "prestaciones sociales"),
    "responsabilidad_civil": ("responsabilidad civil",),
}


def _sin_tildes(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def _norm(texto: str) -> str:
    return re.sub(r"\s+", " ", _sin_tildes((texto or "").lower())).strip()


def parsear_numero(texto):
    if not texto:
        return None
    limpio = re.sub(r"[^\d.,-]", "", texto)
    if not re.search(r"\d", limpio):
        return None

    if "," in limpio and "." in limpio:
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "," in limpio:
        if re.fullmatch(r"\d{1,3}(,\d{3})+", limpio):
            limpio = limpio.replace(",", "")
        else:
            limpio = limpio.replace(",", ".")
    elif "." in limpio:
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", limpio):
            limpio = limpio.replace(".", "")

    try:
        return float(limpio)
    except ValueError:
        return None


def parsear_porcentaje(texto):
    match = re.search(r"(-?\d+(?:[.,]\d+)?)\s*%", texto or "")
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", "."))
    except ValueError:
        return None


def parsear_fecha(texto):
    match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", texto or "")
    if not match:
        return None
    dia, mes, anio = match.groups()
    anio = int(anio)
    if anio < 100:
        anio += 2000
    try:
        return date(anio, int(mes), int(dia)).isoformat()
    except ValueError:
        return None


def _valor_campo(documento, *claves):
    encontrado = campo(documento, *claves)
    return encontrado["valor"].strip() if encontrado else ""


def _bloque_cabecera(documento):
    for bloque in documento.get("bloques", []):
        if bloque.get("tipo") == "cabecera":
            return bloque.get("campos", {})
    return {}


def _numero_contrato(texto):
    match = re.search(
        r"CONTRATO\s+NO\.?\s*([0-9A-Za-z\-]+)",
        (texto or "").replace("\xa0", " "),
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _dias_entre(inicio, fin):
    if not inicio or not fin:
        return None
    try:
        return (date.fromisoformat(fin) - date.fromisoformat(inicio)).days
    except ValueError:
        return None


def construir_contexto(documento):
    tipo_contrato = _valor_campo(documento, "tipo contrato")
    valor_texto = _valor_campo(documento, "valor contrato")
    descripcion = _valor_campo(documento, "descripcion")
    observaciones = _valor_campo(documento, "observaciones")
    proyecto = _valor_campo(documento, "proyecto")

    fecha_inicio = parsear_fecha(_valor_campo(documento, "fecha inicio"))
    fecha_fin = parsear_fecha(
        _valor_campo(documento, "fecha terminacion", "fecha fin")
    )

    forma_pago_campo = campo(documento, "forma de pago")
    if forma_pago_campo is None:
        forma_pago = {"texto": "", "vacia": None, "presente": False, "pagina": None}
    else:
        forma_pago = {
            "texto": forma_pago_campo["valor"].strip(),
            "vacia": forma_pago_campo["vacio"],
            "presente": True,
            "pagina": forma_pago_campo.get("pagina"),
        }

    porcentajes = {
        nombre: parsear_porcentaje(_valor_campo(documento, *claves))
        for nombre, claves in PORCENTAJES.items()
    }
    retenciones = [
        {"tipo": nombre, "valor": valor}
        for nombre, valor in porcentajes.items()
        if nombre.startswith("ret_") and valor is not None
    ]

    cabecera = _bloque_cabecera(documento)
    contratante = {
        "empresa": cabecera.get("empresa", ""),
        "nit": cabecera.get("nit", ""),
        "direccion": cabecera.get("direccion", ""),
        "telefono": cabecera.get("telefono", ""),
        "ciudad": cabecera.get("ciudad", ""),
    }
    contratista = {
        "nombre": _valor_campo(documento, "contratista"),
        "nit": _valor_campo(documento, "nit/cc", "nit cc"),
        "direccion": _valor_campo(documento, "direccion"),
        "telefono": _valor_campo(documento, "telefono"),
        "email": _valor_campo(documento, "email"),
        "ciudad": _valor_campo(documento, "ciudad"),
    }

    objeto = descripcion or proyecto
    texto_operativo = _norm(" ".join((tipo_contrato, objeto, proyecto, observaciones)))
    empresa = _norm(contratante.get("empresa", ""))

    if any(p in empresa for p in ("constructora", "construcciones", "constructor")):
        es_constructora = True
    elif contratante.get("empresa"):
        es_constructora = False
    else:
        es_constructora = None

    polizas = [
        nombre
        for nombre, expresiones in POLIZAS.items()
        if any(expresion in _norm(observaciones) for expresion in expresiones)
    ]

    advertencias = [
        f"OCR no disponible en página {pagina['pagina']}: {pagina['ocr_error']}"
        for pagina in documento.get("paginas", [])
        if pagina.get("ocr_error")
    ]

    return {
        "numero_contrato": _numero_contrato(documento.get("texto", "")),
        "tipo_contrato": tipo_contrato,
        "objeto": objeto,
        "proyecto": proyecto,
        "contratante": contratante,
        "contratista": contratista,
        "valor": parsear_numero(valor_texto),
        "valor_texto": valor_texto,
        "moneda": "COP" if parsear_numero(valor_texto) is not None else None,
        "estado": _valor_campo(documento, "estado"),
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "plazo_dias": _dias_entre(fecha_inicio, fecha_fin),
        "porcentajes": porcentajes,
        "retenciones": retenciones,
        "forma_pago": forma_pago,
        "observaciones": observaciones,
        "polizas_mencionadas": polizas,
        "es_suministro": "suministro" in texto_operativo or "materiales" in texto_operativo,
        "es_instalacion": "instalacion" in texto_operativo or "montaje" in texto_operativo,
        "es_constructora": es_constructora,
        "campos_vacios": list(documento.get("campos_vacios", [])),
        "advertencias": advertencias,
    }
