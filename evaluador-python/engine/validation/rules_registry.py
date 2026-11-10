"""Registro de reglas específicas por criterio.

El markdown define el requisito; este registro elige la implementación
determinista. Los criterios sin regla usan el validador genérico.
"""
from __future__ import annotations

from .gc02 import validar_gc02

REGLAS = {
    "GC-02": validar_gc02,
}


def registrar(criterio_id: str, validador) -> None:
    """Registra o reemplaza el validador de un criterio."""
    REGLAS[criterio_id] = validador


def validador_para(criterio_id: str):
    """Devuelve el validador específico o ``None`` si no existe."""
    return REGLAS.get(criterio_id)
