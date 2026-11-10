"""Capa literal: coincidencia de frases exactas o casi exactas."""
from __future__ import annotations

from .text import normalizar, palabras


def buscar(texto: str, terminos) -> list[dict]:
    """Devuelve las coincidencias literales ordenadas por puntaje (0 a 1)."""
    norm_texto = f" {normalizar(texto)} "
    resultados = []
    for termino in terminos or []:
        norm_termino = normalizar(termino)
        if not norm_termino:
            continue
        partes = palabras(termino)
        if not partes:
            continue
        if f" {norm_termino} " in norm_texto:
            puntaje = 1.0
        else:
            presentes = sum(1 for t in partes if f" {t} " in norm_texto)
            puntaje = presentes / len(partes)
            if puntaje < 0.6:
                continue
        resultados.append({"termino": termino, "score": round(puntaje, 3)})

    resultados.sort(key=lambda item: item["score"], reverse=True)
    return resultados
