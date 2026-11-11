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
from .gc07 import validar_gc07
from .gc08 import validar_gc08
from .gc09 import validar_gc09
from .gc10 import validar_gc10
from .gc11 import validar_gc11
from .gc12 import validar_gc12
from .gc13 import validar_gc13
from .gc14 import validar_gc14
from .gc15 import validar_gc15
from .gc16 import validar_gc16
from .gc17 import validar_gc17
from .gc18 import validar_gc18
from .gc19 import validar_gc19
from .gc24 import validar_gc24

REGLAS = {
    "GC-01": validar_gc01,
    "GC-02": validar_gc02,
    "GC-03": validar_gc03,
    "GC-04": validar_gc04,
    "GC-05": validar_gc05,
    "GC-06": validar_gc06,
    "GC-07": validar_gc07,
    "GC-08": validar_gc08,
    "GC-09": validar_gc09,
    "GC-10": validar_gc10,
    "GC-11": validar_gc11,
    "GC-12": validar_gc12,
    "GC-13": validar_gc13,
    "GC-14": validar_gc14,
    "GC-15": validar_gc15,
    "GC-16": validar_gc16,
    "GC-17": validar_gc17,
    "GC-18": validar_gc18,
    "GC-19": validar_gc19,
    "GC-24": validar_gc24,
}


def registrar(criterio_id: str, validador) -> None:
    """Registra o reemplaza el validador de un criterio."""
    REGLAS[criterio_id] = validador


def validador_para(criterio_id: str):
    """Devuelve el validador específico o ``None`` si no existe."""
    return REGLAS.get(criterio_id)
