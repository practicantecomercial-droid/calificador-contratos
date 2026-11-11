"""Regla determinista para GC-23 (custodia de documentación)."""
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

_FIRMADO = (
    "contrato firmado por la obra",
    "contrato firmado por el cliente",
    "contrato suscrito por la obra",
    "contrato firmado y sellado",
)
_ENTREGA_ADMIN = (
    "documentacion fisica completa",
    "entregar al area administrativa",
    "entrega al area administrativa",
    "documentacion completa al area administrativa",
)
_CUSTODIA = (
    "custodia, control y archivo",
    "asume la custodia",
    "custodia y archivo",
    "control y archivo",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La custodia de la documentación está definida.",
    ESTADO_PARCIAL: "La custodia de la documentación está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la custodia de la documentación.",
}


def _validar_entrega(subrequisito, candidatos, texto):
    if contiene_frase(texto, _ENTREGA_ADMIN):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _ENTREGA_ADMIN),
            "La documentación física completa se entrega al área administrativa.",
        )
    if contiene_frase(texto, ("area administrativa",)) or contiene_frase(
        texto, ("documentacion fisica",)
    ):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, ("area administrativa", "documentacion fisica")),
            "Se menciona entrega o documentación física sin precisar su completitud.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó la entrega al área administrativa.",
    )


def validar_gc23(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la obtención, entrega y custodia de la documentación."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-23.1": lambda sub: resultado_evidencia(
            sub,
            texto,
            _FIRMADO,
            candidatos.get("GC-23.1", []),
            cumple="Se obtiene el contrato firmado por la obra o cliente.",
            parcial="Se menciona contrato firmado sin precisar la firma de la obra.",
            ausente="No se identificó el contrato firmado por la obra o cliente.",
            terminos_parciales=("contrato firmado",),
        ),
        "GC-23.2": lambda sub: _validar_entrega(
            sub, candidatos.get("GC-23.2", []), texto
        ),
        "GC-23.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _CUSTODIA,
            candidatos.get("GC-23.3", []),
            cumple="Administración asume custodia, control y archivo.",
            parcial="Se menciona custodia o archivo sin precisar el control.",
            ausente="No se identificó la custodia por parte de administración.",
            terminos_parciales=("custodia", "archivo"),
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
