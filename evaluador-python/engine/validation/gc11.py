"""Regla determinista para GC-11 (documentos para liquidación de obra)."""
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
    resultado_evidencia,
)
from .generic import combinar_estado
from .operators import contiene_frase

_LIQUIDACION = (
    "liquidacion de la obra",
    "documentos para la liquidacion",
    "requisitos para la liquidacion",
    "cierre de la obra",
    "documentos de liquidacion",
    "para liquidar",
)
_LISTA = (
    "documentos",
    "requisitos",
    "acta",
    "certificados",
    "paz y salvo",
)
_ENTREGA = (
    "documentos entregados",
    "se remiten",
    "se anexan",
    "entrega de documentos",
    "radicados",
    "gestionada la entrega",
)
_SOLICITUD = (
    "solicitar al contratante",
    "solicitud al contratante",
    "requisito faltante",
    "antes del cierre",
    "completar documentacion",
)
_FIRMA = (
    "firma del director comercial",
    "validacion del director comercial",
    "firma del gerente general",
    "aprobacion del director comercial",
    "visto bueno del director comercial",
)
_DIRECTIVO = ("director comercial", "gerente general")

_OBSERVACIONES = {
    ESTADO_CUMPLE: "Los documentos de liquidación están definidos y gestionados.",
    ESTADO_PARCIAL: "Los documentos de liquidación están incompletos.",
    ESTADO_NO_IDENTIFICADO: "No se identificaron documentos para la liquidación.",
    ESTADO_NO_APLICA: "No aplica solicitud de requisitos faltantes.",
}


def _validar_solicitud(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _LIQUIDACION):
        return no_aplica(
            subrequisito, "No se identificó un proceso de liquidación de obra."
        )
    completo = contiene_frase(texto, _LISTA) and contiene_frase(texto, _ENTREGA)
    if completo:
        return no_aplica(
            subrequisito, "La relación de documentos de liquidación está completa."
        )
    if contiene_frase(texto, _SOLICITUD):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _SOLICITUD),
            "Se prevé solicitar al contratante los requisitos faltantes.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _LIQUIDACION),
        "No se prevé solicitar los requisitos faltantes antes del cierre.",
    )


def validar_gc11(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida los documentos y firmas para la liquidación de la obra."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-11.1": lambda sub: resultado_evidencia(
            sub,
            texto,
            _LIQUIDACION,
            candidatos.get("GC-11.1", []),
            cumple="Se identifica una relación expresa de documentos para liquidar.",
            parcial="Se menciona la liquidación sin relación expresa de documentos.",
            ausente="No se identificó una relación de documentos para liquidar.",
            terminos_parciales=("liquidacion", "cierre"),
        ),
        "GC-11.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _ENTREGA,
            candidatos.get("GC-11.2", []),
            cumple="Se evidencia la entrega o gestión de los documentos.",
            parcial="Se mencionan documentos sin acreditar su entrega.",
            ausente="No se identificó la entrega de documentos de liquidación.",
            terminos_parciales=_LISTA,
        ),
        "GC-11.3": lambda sub: _validar_solicitud(
            sub, candidatos.get("GC-11.3", []), texto
        ),
        "GC-11.4": lambda sub: resultado_evidencia(
            sub,
            texto,
            _FIRMA,
            candidatos.get("GC-11.4", []),
            cumple="Se identifica la validación o firma del directivo.",
            parcial="Se menciona al directivo sin acreditar su validación.",
            ausente="No se identificó la validación del director comercial o gerente.",
            terminos_parciales=_DIRECTIVO,
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
