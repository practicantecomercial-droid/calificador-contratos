"""Capa léxica: sinónimos y expresiones equivalentes sin embeddings."""
from __future__ import annotations

from .text import GENERICOS_SEMANTICA_RAIZ, normalizar, tokens


def puntuar(texto: str, terminos):
    """Devuelve ``(puntaje, termino)`` con la mejor coincidencia léxica."""
    norm_texto = f" {normalizar(texto)} "
    tokens_texto = set(tokens(texto))
    mejor_puntaje = 0.0
    mejor_termino = None

    for termino in terminos or []:
        norm_termino = normalizar(termino)
        if not norm_termino:
            continue
        if f" {norm_termino} " in norm_texto:
            puntaje = 1.0
        else:
            tokens_termino = set(tokens(termino))
            if not tokens_termino:
                continue
            distintivos = tokens_termino - GENERICOS_SEMANTICA_RAIZ
            if not (distintivos & tokens_texto) and len(norm_termino.split()) > 1:
                continue
            puntaje = len(tokens_termino & tokens_texto) / len(tokens_termino)
        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            mejor_termino = termino

    return round(mejor_puntaje, 3), mejor_termino
