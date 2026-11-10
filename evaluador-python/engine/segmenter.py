"""Segmentación del documento en unidades de reconocimiento.

Produce unidades auditables (campo, párrafo, cláusula) con página y número de
línea, para que la evidencia pueda citarse con precisión.
"""
from __future__ import annotations

import re

from .document_reader import es_corte, es_etiqueta_valida

_MAX_LINEAS_PARRAFO = 8
_MAX_LINEAS_CLAUSULA = 80

_RE_CLAUSULA = re.compile(
    r"^\s*(?:cl[áa]usula\b|"
    r"(?:primero|segundo|tercero|cuarto|quinto|sexto|séptimo|octavo|noveno|décimo)\b|"
    r"\d{1,2}[.)]\s+[A-ZÁÉÍÓÚ])",
    re.IGNORECASE,
)


def _unidad(numero, tipo, texto, pagina, lineas, **extra):
    unidad = {
        "id": f"U{numero:04d}",
        "tipo": tipo,
        "texto": texto,
        "pagina": pagina,
        "lineas": list(lineas),
    }
    unidad.update(extra)
    return unidad


def _parrafos(lineas):
    bloques = []
    actual = []
    for linea in lineas:
        texto = linea["texto"]
        if (
            not texto
            or es_etiqueta_valida(texto)
            or es_corte(texto)
            or _RE_CLAUSULA.match(texto)
        ):
            if actual:
                bloques.append(actual)
                actual = []
            continue
        actual.append(linea)
        if len(actual) >= _MAX_LINEAS_PARRAFO:
            bloques.append(actual)
            actual = []
    if actual:
        bloques.append(actual)

    return [
        {
            "texto": " ".join(item["texto"] for item in bloque),
            "pagina": bloque[0]["pagina"],
            "lineas": [item["n"] for item in bloque],
        }
        for bloque in bloques
    ]


def _clausulas(lineas):
    clausulas = []
    i = 0
    while i < len(lineas):
        if not _RE_CLAUSULA.match(lineas[i]["texto"]):
            i += 1
            continue

        inicio = i
        i += 1
        while (
            i < len(lineas)
            and i - inicio < _MAX_LINEAS_CLAUSULA
            and not _RE_CLAUSULA.match(lineas[i]["texto"])
        ):
            i += 1

        bloque = lineas[inicio:i]
        clausulas.append({
            "texto": " ".join(item["texto"] for item in bloque if item["texto"]),
            "titulo": lineas[inicio]["texto"],
            "pagina": lineas[inicio]["pagina"],
            "lineas": [item["n"] for item in bloque],
        })
    return clausulas


def segmentar(documento):
    """Devuelve la lista de unidades (campo, párrafo, cláusula) del documento."""
    unidades = []
    numero = 0

    for campo in documento.get("campos_lista", []):
        numero += 1
        texto = f"{campo['etiqueta']}: {campo['valor']}".strip()
        unidades.append(_unidad(
            numero,
            "campo",
            texto,
            campo.get("pagina"),
            campo.get("lineas", []),
            etiqueta=campo["etiqueta"],
            clave=campo["clave"],
            vacio=campo.get("vacio", False),
        ))

    for parrafo in _parrafos(documento.get("lineas", [])):
        numero += 1
        unidades.append(_unidad(
            numero, "parrafo", parrafo["texto"], parrafo["pagina"], parrafo["lineas"]
        ))

    for clausula in _clausulas(documento.get("lineas", [])):
        numero += 1
        unidades.append(_unidad(
            numero,
            "clausula",
            clausula["texto"],
            clausula["pagina"],
            clausula["lineas"],
            titulo=clausula["titulo"],
        ))

    return unidades


def unidades_por_tipo(unidades, tipo):
    return [unidad for unidad in unidades if unidad["tipo"] == tipo]
