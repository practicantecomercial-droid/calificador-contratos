"""Regla determinista para GC-07 (referencia a la cotización)."""
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

_COTIZACION = ("cotizacion", "propuesta economica", "oferta")
_REFERENCIA = (
    "numero de cotizacion",
    "cotizacion numero",
    "cotizacion no",
    "codigo de cotizacion",
    "referencia de la cotizacion",
    "cotizacion referencia",
)
_FECHA = (
    "fecha de elaboracion",
    "fecha de emision",
    "fecha de la cotizacion",
    "elaborada el",
    "emitida el",
)
_POLIZAS = ("poliza", "polizas", "cuenta de cobro", "cuentas de cobro")
_COINCIDENCIA = (
    "misma referencia",
    "coincide con la cotizacion",
    "coincidencia de referencia",
    "referencia de la cotizacion en la poliza",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "El contrato referencia la cotización y su fecha.",
    ESTADO_PARCIAL: "La referencia a la cotización está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó referencia a la cotización.",
    ESTADO_NO_APLICA: "No aplica la coincidencia con pólizas o cuentas de cobro.",
}


def _validar_coincidencia(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _POLIZAS):
        return no_aplica(
            subrequisito,
            "No se identificaron pólizas ni cuentas de cobro disponibles.",
        )
    if contiene_frase(texto, _COINCIDENCIA):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _COINCIDENCIA),
            "La referencia de la cotización coincide en pólizas o cuentas de cobro.",
        )
    if contiene_frase(texto, _COTIZACION):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _POLIZAS + _COTIZACION),
            "Se mencionan pólizas o cuentas de cobro sin acreditar la coincidencia.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        candidatos_con(candidatos, _POLIZAS),
        "Se mencionan pólizas o cuentas de cobro sin acreditar la coincidencia.",
    )


def validar_gc07(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la referencia expresa a la cotización en el contrato."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-07.1": lambda sub: resultado_evidencia(
            sub,
            texto,
            _REFERENCIA,
            candidatos.get("GC-07.1", []),
            cumple="El contrato identifica la cotización por número o código.",
            parcial="Se menciona la cotización sin número o código.",
            ausente="No se identificó la referencia a la cotización.",
            terminos_parciales=_COTIZACION,
        ),
        "GC-07.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _FECHA,
            candidatos.get("GC-07.2", []),
            cumple="El contrato indica la fecha de elaboración de la cotización.",
            parcial="Se menciona la cotización sin su fecha de elaboración.",
            ausente="No se identificó la fecha de la cotización.",
            terminos_parciales=_COTIZACION,
        ),
        "GC-07.3": lambda sub: _validar_coincidencia(
            sub, candidatos.get("GC-07.3", []), texto
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
