"""Regla determinista para GC-22 (entrega física de documentos en CEDI)."""
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

_CEDI = (
    "entrega fisica en el cedi",
    "entregado en el cedi",
    "cedi",
    "centro de distribucion",
)
_FIRMA = (
    "firma del asistente de despacho",
    "firma del jefe de cedi",
    "formato de entrega",
    "formato indicado",
)
_RECEPCION = (
    "evidencia de recepcion",
    "acuse de recibo",
    "recibido conforme",
    "sello de recibido",
    "constancia de recepcion",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La entrega física en CEDI está evidenciada.",
    ESTADO_PARCIAL: "La entrega física en CEDI está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la entrega física en CEDI.",
}


def _validar_entrega(subrequisito, candidatos, texto):
    if contiene_frase(texto, _CEDI):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _CEDI),
            "Se identifica la entrega física en el CEDI.",
        )
    if contiene_frase(texto, ("entrega fisica",)):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, ("entrega fisica",)),
            "Se menciona entrega física sin precisar el CEDI.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó la entrega física en el CEDI.",
    )


def validar_gc22(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la entrega física, firma y recepción en CEDI."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-22.1": lambda sub: _validar_entrega(
            sub, candidatos.get("GC-22.1", []), texto
        ),
        "GC-22.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _FIRMA,
            candidatos.get("GC-22.2", []),
            cumple="Se identifica la firma del asistente de despacho o jefe de CEDI.",
            parcial="Se menciona firma sin precisar el formato indicado.",
            ausente="No se identificó la firma de recibido en CEDI.",
            terminos_parciales=("firma", "cedi", "despacho"),
        ),
        "GC-22.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _RECEPCION,
            candidatos.get("GC-22.3", []),
            cumple="Se evidencia la recepción de los documentos.",
            parcial="Se menciona recepción sin evidencia documental.",
            ausente="No se identificó evidencia de recepción.",
            terminos_parciales=("recepcion",),
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
