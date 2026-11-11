"""Regla determinista para GC-08 (multas y cláusulas penales)."""
from __future__ import annotations

from ..schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_CUMPLE,
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

_MULTAS = ("clausula penal", "multa", "penalidad", "sancion")
_BILATERAL = (
    "bilateral",
    "mutuo acuerdo",
    "reciproca",
    "ambas partes",
    "acuerdo entre las partes",
    "se aplicara a ambas partes",
)
_UNILATERAL = (
    "unilateral",
    "solo al contratista",
    "exclusivamente al contratista",
    "a cargo del contratista",
)
_RECIPROCIDAD = (
    "obligaciones reciprocas",
    "consecuencias reciprocas",
    "mutuas",
    "reciprocidad",
    "derechos y obligaciones para ambas partes",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "Las multas o cláusulas penales se aplican de forma bilateral.",
    ESTADO_PARCIAL: "Las multas o cláusulas penales no acreditan bilateralidad.",
    ESTADO_NO_CUMPLE: "Las multas o cláusulas penales son unilaterales.",
    ESTADO_NO_IDENTIFICADO: "No se identificaron multas ni cláusulas penales.",
    ESTADO_NO_APLICA: "El contrato no contempla multas ni cláusulas penales.",
}


def _validar_existencia(subrequisito, candidatos, texto):
    if contiene_frase(texto, _MULTAS):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _MULTAS),
            "Se identifican multas o cláusulas penales.",
        )
    return no_aplica(
        subrequisito, "El contrato no contempla multas ni cláusulas penales."
    )


def _validar_bilateralidad(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _MULTAS):
        return no_aplica(
            subrequisito, "No aplica bilateralidad sin multas o cláusulas penales."
        )
    if contiene_frase(texto, _UNILATERAL):
        return resultado(
            subrequisito,
            ESTADO_NO_CUMPLE,
            candidatos_con(candidatos, _UNILATERAL),
            "Las multas o cláusulas penales se aplican solo al contratista.",
        )
    if contiene_frase(texto, _BILATERAL):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _BILATERAL),
            "Las multas o cláusulas penales pueden aplicarse bilateralmente.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _MULTAS),
        "Se identifican multas sin acreditar su bilateralidad.",
    )


def _validar_reciprocidad(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _MULTAS):
        return no_aplica(
            subrequisito, "No aplica reciprocidad sin multas o cláusulas penales."
        )
    if contiene_frase(texto, _RECIPROCIDAD):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _RECIPROCIDAD),
            "Las obligaciones y consecuencias se expresan de manera recíproca.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _MULTAS),
        "No se acredita reciprocidad de obligaciones y consecuencias.",
    )


def validar_gc08(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la existencia y bilateralidad de multas y cláusulas penales."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-08.1": lambda sub: _validar_existencia(
            sub, candidatos.get("GC-08.1", []), texto
        ),
        "GC-08.2": lambda sub: _validar_bilateralidad(
            sub, candidatos.get("GC-08.2", []), texto
        ),
        "GC-08.3": lambda sub: _validar_reciprocidad(
            sub, candidatos.get("GC-08.3", []), texto
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
