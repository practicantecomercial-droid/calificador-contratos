"""Registro de reglas específicas por criterio.

El markdown define el requisito; este registro elige la implementación
determinista. Los criterios sin regla usan el validador genérico.
"""
from __future__ import annotations

from .gc01 import validar_gc01
from .gc02 import validar_gc02
from .gc03 import validar_gc03
from .gc04 import validar_gc04
from .gc05 import validar_gc05
from .gc06 import validar_gc06
from .gc09 import validar_gc09
from .gc14 import validar_gc14
from .gc16 import validar_gc16
from .gc24 import validar_gc24

REGLAS = {
    "GC-01": validar_gc01,
    "GC-02": validar_gc02,
    "GC-03": validar_gc03,
    "GC-04": validar_gc04,
    "GC-05": validar_gc05,
    "GC-06": validar_gc06,
    "GC-09": validar_gc09,
    "GC-14": validar_gc14,
    "GC-16": validar_gc16,
    "GC-24": validar_gc24,
}


def registrar(criterio_id: str, validador) -> None:
    """Registra o reemplaza el validador de un criterio."""
    REGLAS[criterio_id] = validador


def validador_para(criterio_id: str):
    """Devuelve el validador específico o ``None`` si no existe."""
    return REGLAS.get(criterio_id)
