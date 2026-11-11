"""Regla determinista para GC-12 (devolución del retenido)."""
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
)
from .generic import combinar_estado
from .operators import contiene_frase

_RETENIDO = ("retenido", "retencion", "retenciones", "retener")
_ACTIVACION = (
    "devolucion del retenido",
    "liberacion del retenido",
    "devolucion de la retencion",
    "liberacion de la retencion",
    "se devolvera",
    "se liberara",
    "a la liquidacion",
    "al cumplimiento",
    "al termino del contrato",
)
_DOCUMENTOS = (
    "acta de liquidacion",
    "paz y salvo",
    "certificacion",
    "cuenta de cobro",
    "documentos requeridos",
    "documentos para la devolucion",
)
_PLAZO = (
    "plazo",
    "dentro de",
    "dias siguientes",
    "meses siguientes",
    "termino de",
)
_CONDICIONES = (
    "condiciones de liberacion",
    "condiciones de devolucion",
    "previo cumplimiento",
    "una vez",
    "siempre que",
    "sujeto a",
    "a satisfaccion",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La devolución del retenido está definida en sus condiciones.",
    ESTADO_PARCIAL: "La devolución del retenido está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la devolución del retenido.",
}


def _validar_condicion(subrequisito, candidatos, texto, terminos, mensaje):
    if not contiene_frase(texto, _RETENIDO):
        return resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificó retención alguna en el contrato.",
        )
    if contiene_frase(texto, terminos):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, terminos),
            mensaje,
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _RETENIDO),
        "Se identifica retención sin precisar este aspecto.",
    )


def validar_gc12(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida las condiciones de devolución del valor retenido."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-12.1": lambda sub: _validar_condicion(
            sub,
            candidatos.get("GC-12.1", []),
            texto,
            _ACTIVACION,
            "Se identifica qué activa la devolución del retenido.",
        ),
        "GC-12.2": lambda sub: _validar_condicion(
            sub,
            candidatos.get("GC-12.2", []),
            texto,
            _DOCUMENTOS,
            "Se identifican los documentos requeridos para la devolución.",
        ),
        "GC-12.3": lambda sub: _validar_condicion(
            sub,
            candidatos.get("GC-12.3", []),
            texto,
            _PLAZO,
            "Se identifica el plazo para la devolución del retenido.",
        ),
        "GC-12.4": lambda sub: _validar_condicion(
            sub,
            candidatos.get("GC-12.4", []),
            texto,
            _CONDICIONES,
            "Se identifican las condiciones de liberación del retenido.",
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
