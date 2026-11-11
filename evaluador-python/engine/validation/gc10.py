"""Regla determinista para GC-10 (ajuste de valores por demora)."""
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

_DEMORA = (
    "demora",
    "retraso",
    "atraso",
    "fecha pactada",
    "plazo pactado",
    "causas ajenas",
)
_AJUSTE = (
    "ajuste de valores",
    "reajuste de precios",
    "actualizacion de precios",
    "ajuste de precios",
    "reajuste",
)
_MERCADO = (
    "variacion del mercado",
    "variaciones del mercado",
    "variaciones de mercado",
    "precios de mercado",
    "indice de precios",
    "ipc",
    "conforme al mercado",
    "condiciones del mercado",
)
_ANEXO = (
    "anexo complementario",
    "anexo de ajuste",
    "anexo indicado",
    "jefe administrativo",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "Se contempla el ajuste de valores por demora y variación de mercado.",
    ESTADO_PARCIAL: "El ajuste de valores por demora está incompleto.",
    ESTADO_NO_IDENTIFICADO: "No se identificó el ajuste de valores por demora.",
    ESTADO_NO_APLICA: "No se contempla ajuste de valores por demora.",
}


def _validar_posibilidad(subrequisito, candidatos, texto):
    if contiene_frase(texto, _AJUSTE) and contiene_frase(texto, _DEMORA):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _AJUSTE + _DEMORA),
            "Se contempla el ajuste de valores por demora en la ejecución.",
        )
    if contiene_frase(texto, _DEMORA) or contiene_frase(texto, _AJUSTE):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _DEMORA + _AJUSTE),
            "Se menciona demora o ajuste sin precisar la posibilidad completa.",
        )
    return no_aplica(
        subrequisito, "No se contempla ajuste de valores por demora."
    )


def validar_gc10(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida el ajuste de valores por demora y variación de mercado."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-10.1": lambda sub: _validar_posibilidad(
            sub, candidatos.get("GC-10.1", []), texto
        ),
        "GC-10.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _MERCADO,
            candidatos.get("GC-10.2", []),
            cumple="El ajuste se relaciona con variaciones del mercado.",
            parcial="Se menciona ajuste sin relacionarlo con el mercado.",
            ausente="No se identificó la relación del ajuste con el mercado.",
            terminos_parciales=_AJUSTE,
        ),
        "GC-10.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _ANEXO,
            candidatos.get("GC-10.3", []),
            cumple="Se identifica el anexo complementario con el jefe administrativo.",
            parcial="Se menciona un anexo sin verificar su gestión.",
            ausente="No se identificó el anexo complementario de ajuste.",
            terminos_parciales=("anexo",),
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
