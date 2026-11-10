"""Capa contextual: negaciones, condiciones, sujeto y contradicciones."""
from __future__ import annotations

import re

from ..schema import MARCADORES_CONTRADICCION
from .text import normalizar

_MARCADORES = {
    categoria: tuple(normalizar(marcador) for marcador in marcadores)
    for categoria, marcadores in MARCADORES_CONTRADICCION.items()
}

_SUJETOS = (
    "contratante", "contratista", "proveedor", "cliente",
    "interdoors", "constructor", "constructora",
)

_RE_RETENCION = re.compile(r"\bret(?:encion)?\s*(?:de\s+|del\s+)?anticipo\b")
_RE_GARANTIA_ANTICIPO = re.compile(
    r"\b(?:poliza|garantia|seguro)\s+de\s+[a-z ]{0,40}anticipo\b"
)


def _en(texto: str, marcador: str) -> bool:
    return bool(re.search(rf"\b{re.escape(marcador)}\b", texto))


def _hay_negacion(ventana: str) -> bool:
    marcadores = _MARCADORES["negacion"]
    if "no obstante" in ventana:
        marcadores = tuple(m for m in marcadores if m != "no")
    return any(_en(ventana, marcador) for marcador in marcadores)


def _sujeto(ventana: str, posicion: int):
    antes = ventana[:posicion]
    mejor = None
    mejor_pos = -1
    for sujeto in _SUJETOS:
        for coincidencia in re.finditer(rf"\b{re.escape(sujeto)}\b", antes):
            if coincidencia.start() > mejor_pos:
                mejor = sujeto
                mejor_pos = coincidencia.start()
    return mejor


def _es_retencion(ventana: str) -> bool:
    return bool(_RE_RETENCION.search(ventana))


def _es_garantia_anticipo(ventana: str, termino: str) -> bool:
    """True si todas las menciones del término están dentro de una póliza/garantía."""
    if not termino:
        return False
    posiciones = [
        coincidencia.start()
        for coincidencia in re.finditer(rf"\b{re.escape(termino)}\b", ventana)
    ]
    if not posiciones:
        return False
    rangos = [
        (coincidencia.start(), coincidencia.end())
        for coincidencia in _RE_GARANTIA_ANTICIPO.finditer(ventana)
    ]
    dentro = [
        posicion for posicion in posiciones
        if any(inicio <= posicion <= fin for inicio, fin in rangos)
    ]
    return bool(dentro) and len(dentro) == len(posiciones)


def _contradicciones(ventana: str, subrequisito) -> list[str]:
    requisito = normalizar(subrequisito.get("texto", ""))
    hallazgos = []

    if "anticipo" in requisito and _es_retencion(ventana):
        hallazgos.append("retencion_no_es_anticipo")

    if "entrega" in requisito and "instalacion" in ventana:
        if (
            "contra instalacion" in ventana
            or "despues de la instalacion" in ventana
            or "una vez instalado" in ventana
        ):
            hallazgos.append("evento_distinto")

    if "credito" in requisito and (
        "contado" in ventana or "pago inmediato" in ventana
    ):
        hallazgos.append("credito_no_otorgado")

    return sorted(set(hallazgos))


def analizar(texto: str, termino: str, subrequisito) -> dict:
    """Analiza la ventana alrededor de la coincidencia y calcula un ajuste."""
    norm = normalizar(texto)
    term = normalizar(termino)
    posicion = norm.find(term) if term else -1
    if posicion < 0:
        posicion = 0
        inicio = 0
        ventana = norm
    else:
        inicio = max(0, posicion - 120)
        fin = min(len(norm), posicion + len(term) + 120)
        ventana = norm[inicio:fin]
    posicion_ventana = posicion - inicio
    requisito = normalizar(subrequisito.get("texto", ""))

    flags = {
        "negado": _hay_negacion(ventana),
        "exclusivo": any(_en(ventana, m) for m in _MARCADORES["exclusividad"]),
        "condicional": (
            any(_en(ventana, m) for m in _MARCADORES["condicion"])
            or _en(ventana, "si")
        ),
        "excepcion": any(_en(ventana, m) for m in _MARCADORES["excepcion"]),
        "aprobacion": any(_en(ventana, m) for m in _MARCADORES["aprobacion"]),
        "temporal": any(_en(ventana, m) for m in _MARCADORES["temporalidad"]),
        "sujeto": _sujeto(ventana, posicion_ventana),
        "es_retencion": _es_retencion(ventana),
        "es_garantia_anticipo": _es_garantia_anticipo(ventana, term),
    }

    contradicciones = _contradicciones(ventana, subrequisito)

    ajuste = 1.0
    if flags["negado"]:
        ajuste *= 0.4
    if flags["excepcion"]:
        ajuste *= 0.8
    if flags["aprobacion"]:
        ajuste *= 0.9
    if flags["exclusivo"]:
        ajuste *= 0.95
    if flags["condicional"]:
        ajuste *= 0.95
    if flags["es_retencion"] and "anticipo" in requisito:
        ajuste *= 0.3
    if flags["es_garantia_anticipo"] and "anticipo" in requisito:
        ajuste *= 0.3
    if "evento_distinto" in contradicciones:
        ajuste *= 0.3
    if "credito_no_otorgado" in contradicciones:
        ajuste *= 0.4

    return {
        "flags": flags,
        "ajuste": round(ajuste, 3),
        "contradicciones": contradicciones,
    }
