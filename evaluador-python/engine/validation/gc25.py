"""Regla determinista para GC-25 (anexo de garantía de Interdoors)."""
from __future__ import annotations

from ..schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
)
from .common import (
    candidatos_con,
    finalizar,
    observacion_criterio,
    resultado,
    resultado_evidencia,
)
from .generic import combinar_estado

_ANEXO = (
    "anexo de garantia",
    "documento de garantia de interdoors",
    "garantia de interdoors",
    "anexo de garantia de interdoors",
)
_INCORPORACION = (
    "anexo forma parte integral",
    "incorporado al contrato",
    "parte integral del contrato",
    "se anexa garantia",
    "adjunto al contrato",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "El anexo de garantía está incorporado al contrato.",
    ESTADO_PARCIAL: "El anexo de garantía está incompleto.",
    ESTADO_NO_IDENTIFICADO: "No se identificó el anexo de garantía.",
}


def validar_gc25(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida el anexo de garantía de Interdoors y su incorporación."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-25.1": lambda sub: resultado_evidencia(
            sub,
            texto,
            _ANEXO,
            candidatos.get("GC-25.1", []),
            cumple="El documento de garantía de Interdoors está incorporado o adjunto.",
            parcial="Se menciona garantía sin acreditar el anexo de Interdoors.",
            ausente="No se identificó el anexo de garantía de Interdoors.",
            terminos_parciales=("garantia",),
        ),
        "GC-25.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _INCORPORACION,
            candidatos.get("GC-25.2", []),
            cumple="Se evidencia la incorporación del anexo como parte integral.",
            parcial="Se menciona anexo sin acreditar su incorporación.",
            ausente="No se identificó evidencia de incorporación del anexo.",
            terminos_parciales=("anexo", "adjunto"),
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
