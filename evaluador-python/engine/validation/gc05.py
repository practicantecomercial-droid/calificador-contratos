"""Regla determinista para GC-05 (facturación de la instalación)."""
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
from .operators import contiene_frase

_INSTALACION = ("instalacion", "montaje", "mano de obra de instalacion")
_CORTES = (
    "cortes semanales",
    "corte semanal",
    "acta semanal",
    "medicion semanal",
    "facturacion semanal",
    "avance semanal",
    "cortes de obra",
)
_AVANCE = (
    "avance efectivamente realizado",
    "actividades ejecutadas",
    "entrega efectuada",
    "avance realizado",
    "obra ejecutada",
    "avance de obra",
)
_RECEPCION = (
    "disponibilidad de recepcion",
    "personal para recibir",
    "acceso y recepcion",
    "recibido por la obra",
    "recepcion en obra",
    "disponibilidad para recibir",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La facturación de la instalación está soportada en cortes y avance.",
    ESTADO_PARCIAL: "La facturación de la instalación no está plenamente precisada.",
    ESTADO_NO_IDENTIFICADO: "No se identificaron condiciones de facturación de la instalación.",
}


def _validar_cortes(subrequisito, candidatos, texto):
    if contiene_frase(texto, _CORTES):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _CORTES),
            "Se identifican cortes semanales de facturación.",
        )
    if contiene_frase(texto, _INSTALACION) and contiene_frase(
        texto, ("facturacion", "corte", "avance")
    ):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _INSTALACION),
            "Se menciona facturación de instalación sin cortes semanales.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificaron cortes semanales de instalación.",
    )


def validar_gc05(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la facturación de la instalación por cortes y avance."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-05.1": lambda sub: _validar_cortes(
            sub, candidatos.get("GC-05.1", []), texto
        ),
        "GC-05.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _AVANCE,
            candidatos.get("GC-05.2", []),
            cumple="Los cortes se basan en el avance efectivamente realizado.",
            parcial="Se menciona avance sin precisar su vínculo con los cortes.",
            ausente="No se identificó el avance efectivo de la instalación.",
            terminos_parciales=("corte", "avance"),
        ),
        "GC-05.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _RECEPCION,
            candidatos.get("GC-05.3", []),
            cumple="Se reconoce la disponibilidad de recepción por parte de la obra.",
            parcial="Se menciona la recepción sin precisar la disponibilidad de la obra.",
            ausente="No se identificó la disponibilidad de recepción.",
            terminos_parciales=("recepcion", "obra"),
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
