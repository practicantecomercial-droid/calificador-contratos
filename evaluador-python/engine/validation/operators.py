"""Operadores deterministas reutilizables por las reglas de validación."""
from __future__ import annotations

import re
import unicodedata

from ..recognition.text import normalizar
from ..schema import UMBRALES

_RE_PORCENTAJE = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")
_RE_NUMERO = re.compile(r"\d[\d.,]*")

_PALABRAS_NUMERO = {
    "diez": 10, "veinte": 20, "treinta": 30, "cuarenta": 40,
    "cincuenta": 50, "sesenta": 60, "setenta": 70, "ochenta": 80,
    "noventa": 90, "cien": 100,
}


def _texto_numerico(texto: str) -> str:
    """Minúsculas y sin tildes, conservando cifras y separadores numéricos."""
    descompuesto = unicodedata.normalize("NFKD", texto or "")
    sin_tildes = "".join(c for c in descompuesto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sin_tildes.lower()).strip()


def _a_float(token: str):
    token = (token or "").strip(".,")
    if not token:
        return None
    if "," in token and "." in token:
        if token.rfind(",") > token.rfind("."):
            token = token.replace(".", "").replace(",", ".")
        else:
            token = token.replace(",", "")
    elif "," in token:
        partes = token.split(",")
        if len(partes) == 2 and len(partes[1]) <= 2:
            token = token.replace(",", ".")
        else:
            token = token.replace(",", "")
    elif "." in token:
        partes = token.split(".")
        if len(partes) > 2 or len(partes[1]) == 3:
            token = token.replace(".", "")
    try:
        return float(token)
    except ValueError:
        return None


def numeros(texto: str) -> list[float]:
    """Extrae números tolerando separadores de miles y decimales."""
    return [
        valor
        for valor in (
            _a_float(token) for token in _RE_NUMERO.findall(_texto_numerico(texto))
        )
        if valor is not None
    ]


def porcentajes(texto: str) -> list[float]:
    """Extrae porcentajes numéricos (``40%``) y escritos (``cuarenta por ciento``)."""
    norm = _texto_numerico(texto)
    valores = []
    for coincidencia in _RE_PORCENTAJE.finditer(norm):
        valor = _a_float(coincidencia.group(1))
        if valor is not None:
            valores.append(valor)
    for palabra, valor in _PALABRAS_NUMERO.items():
        if re.search(rf"\b{palabra}\s+por\s+ciento\b", norm):
            valores.append(float(valor))
    return valores


def contiene_porcentaje(texto: str, valor: float, tolerancia=0.5) -> bool:
    """True si el texto contiene el porcentaje o su fracción decimal (0,40)."""
    if any(abs(porcentaje - valor) <= tolerancia for porcentaje in porcentajes(texto)):
        return True
    return any(
        abs(numero - valor / 100) <= 0.005 for numero in numeros(texto)
    )


def contiene_frase(texto: str, frases) -> bool:
    norm = normalizar(texto)
    return any(normalizar(frase) in norm for frase in frases)


def clasificar_score(score: float) -> str:
    if score >= UMBRALES["alta"]:
        return "alta"
    if score >= UMBRALES["probable"]:
        return "probable"
    if score >= UMBRALES["debil"]:
        return "debil"
    return "nula"
