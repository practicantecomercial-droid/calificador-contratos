"""Fase de validación: convierte candidatos en estados auditables.

Las reglas específicas viven en ``rules_registry``; el validador genérico
cubre los criterios que aún no tienen operadores deterministas.
"""
from __future__ import annotations

from ..context import construir_contexto
from ..schema import (
    ALCANCE_DOCUMENTAL,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
)
from .common import marcar_evidencia_externa
from .generic import validar_criterio_generico
from .rules_registry import validador_para

__all__ = [
    "validar_criterio",
    "validar_documento",
]


def _texto_documento(documento) -> str:
    if documento is None:
        return ""
    if isinstance(documento, str):
        return documento
    return documento.get("texto", "")


def validar_criterio(
    criterio,
    reconocimiento,
    contexto=None,
    texto_documento="",
):
    """Valida un criterio con su regla específica o el validador genérico."""
    validador = validador_para(criterio.get("criterio_id"))
    if validador is None:
        resultado = validar_criterio_generico(
            criterio,
            reconocimiento,
            contexto=contexto,
            texto_documento=texto_documento,
        )
    else:
        resultado = validador(
            criterio,
            reconocimiento,
            contexto=contexto,
            texto_documento=texto_documento,
        )
    if (
        criterio.get("requiere_evidencia_externa")
        and resultado.get("alcance") == ALCANCE_DOCUMENTAL
        and resultado.get("estado") in (ESTADO_NO_IDENTIFICADO, ESTADO_PARCIAL)
    ):
        marcar_evidencia_externa(resultado, criterio)
    return resultado


def validar_documento(
    base,
    reconocimiento,
    *,
    contexto=None,
    documento=None,
    criterios=None,
):
    """Valida los criterios reconocidos de un documento."""
    if contexto is None and documento is not None:
        contexto = construir_contexto(documento)
    texto = _texto_documento(documento)
    seleccionados = set(criterios) if criterios is not None else None

    resultados = {}
    for criterio in base.get("criterios", []):
        criterio_id = criterio["criterio_id"]
        if seleccionados is not None and criterio_id not in seleccionados:
            continue
        reconocido = reconocimiento.get("criterios", {}).get(criterio_id)
        if reconocido is None:
            continue
        resultados[criterio_id] = validar_criterio(
            criterio,
            reconocido,
            contexto=contexto,
            texto_documento=texto,
        )
    return {"criterios": resultados, "contexto": contexto or {}}
