"""Regla determinista para GC-13 (reajuste por vigencia posterior)."""
from __future__ import annotations

from ..schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
)
from .common import (
    candidatos_con,
    finalizar,
    no_aplica,
    observacion_criterio,
    resultado,
)
from .generic import combinar_estado
from .operators import contiene_frase

_VIGENCIA_POSTERIOR = (
    "vigencia posterior",
    "ano calendario posterior",
    "ejecucion en el ano siguiente",
    "ejecucion en vigencia posterior",
    "siguiente ano calendario",
    "ano siguiente",
    "vigencia siguiente",
)
_REAJUSTE = (
    "solicitud de reajuste",
    "prevision de reajuste",
    "reajuste conforme al mercado",
    "reajuste de precios",
    "actualizacion de precios",
)
_APROBACION = (
    "aprobacion de la direccion comercial",
    "autorizacion de la direccion comercial",
    "no reajustar",
    "no se reajustara",
    "aprobacion expresa",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "Se prevé el reajuste para ejecución en vigencia posterior.",
    ESTADO_PARCIAL: "La previsión de reajuste por vigencia posterior está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la vigencia de ejecución.",
    ESTADO_NO_APLICA: "La ejecución no se proyecta en una vigencia posterior.",
}


def _validar_vigencia(subrequisito, candidatos, texto):
    if contiene_frase(texto, _VIGENCIA_POSTERIOR):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _VIGENCIA_POSTERIOR),
            "Se identifica ejecución en un año calendario posterior.",
        )
    if contiene_frase(texto, ("vigencia", "ano", "cotizacion")):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, ("vigencia", "ano")),
            "Se menciona la vigencia sin precisar si la ejecución es posterior.",
        )
    return no_aplica(
        subrequisito, "No se identificó ejecución en vigencia posterior."
    )


def _validar_reajuste(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _VIGENCIA_POSTERIOR):
        return no_aplica(
            subrequisito, "No aplica reajuste sin ejecución en vigencia posterior."
        )
    if contiene_frase(texto, _REAJUSTE) or contiene_frase(texto, _APROBACION):
        terminos = _REAJUSTE + _APROBACION
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, terminos),
            "Se prevé reajuste o aprobación expresa para la vigencia posterior.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _VIGENCIA_POSTERIOR),
        "La ejecución es posterior y no se acredita reajuste ni aprobación.",
    )


def validar_gc13(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la previsión de reajuste por ejecución en vigencia posterior."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-13.1": lambda sub: _validar_vigencia(
            sub, candidatos.get("GC-13.1", []), texto
        ),
        "GC-13.2": lambda sub: _validar_reajuste(
            sub, candidatos.get("GC-13.2", []), texto
        ),
    }

    resultados = [
        validadores[subrequisito_id](subrequisitos[subrequisito_id])
        for subrequisito_id in validadores
        if subrequisito_id in subrequisitos
    ]
    estado = combinar_estado(resultados)
    return finalizar(
        criterio,
        resultados,
        contexto,
        observacion=observacion_criterio(estado, resultados, _OBSERVACIONES),
    )
