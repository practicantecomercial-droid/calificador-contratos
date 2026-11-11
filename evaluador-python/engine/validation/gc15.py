"""Regla determinista para GC-15 (revisión y aprobación del contrato)."""
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

_REVISION = (
    "revision del director comercial",
    "revisado por el director comercial",
    "visto bueno del director comercial",
    "aprobacion del director comercial",
)
_FIRMA = (
    "firma del director comercial",
    "firmado por el director comercial",
    "firma director comercial",
)
_GERENCIA = (
    "aprobacion de gerencia",
    "firma de gerencia",
    "remitido a gerencia",
    "aprobacion final de gerencia",
    "gerencia general",
)
_DIRECTOR = ("director comercial",)
_GERENTE = ("gerencia",)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "El contrato evidencia revisión, firma y aprobación de gerencia.",
    ESTADO_PARCIAL: "La revisión y aprobación del contrato está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la revisión y aprobación del contrato.",
}


def validar_gc15(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la revisión del director comercial y la aprobación de gerencia."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-15.1": lambda sub: resultado_evidencia(
            sub,
            texto,
            _REVISION,
            candidatos.get("GC-15.1", []),
            cumple="Se identifica la revisión previa del director comercial.",
            parcial="Se menciona al director comercial sin acreditar la revisión.",
            ausente="No se identificó la revisión del director comercial.",
            terminos_parciales=_DIRECTOR,
        ),
        "GC-15.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _FIRMA,
            candidatos.get("GC-15.2", []),
            cumple="Se identifica la firma del director comercial.",
            parcial="Se menciona al director comercial sin acreditar su firma.",
            ausente="No se identificó la firma del director comercial.",
            terminos_parciales=_DIRECTOR,
        ),
        "GC-15.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _GERENCIA,
            candidatos.get("GC-15.3", []),
            cumple="El contrato se remite a gerencia para aprobación final.",
            parcial="Se menciona gerencia sin acreditar la aprobación final.",
            ausente="No se identificó la aprobación final de gerencia.",
            terminos_parciales=_GERENTE,
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
