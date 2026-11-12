"""Regla determinista para GC-06 (cotización)."""
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

_COTIZACION = ("cotizacion", "oferta", "propuesta economica", "presupuesto comercial")
_PRECIOS = ("precios", "valores unitarios", "tarifas", "valor ofertado")
_CANTIDADES = ("cantidades", "unidades", "numero de elementos")
_CORRESPONDENCIA_PRECIOS = (
    "precios de la cotizacion",
    "precios y cantidades",
    "mismos precios",
    "precios coinciden",
    "concordancia de precios",
    "valor ofertado",
)
_CORRESPONDENCIA_CANTIDADES = (
    "cantidades de la cotizacion",
    "cantidades y precios",
    "precios y cantidades",
    "correspondencia de precios y cantidades",
    "cantidades coinciden",
    "unidades ofertadas",
    "concordancia de cantidades",
)
_VIGENCIA_30 = (
    "vigencia de 30 dias",
    "validez de 30 dias",
    "treinta dias calendario",
    "30 dias calendario",
)
_VIGENCIA = ("vigencia", "validez", "plazo de aceptacion")
_VERIFICACION = (
    "verificacion de precios",
    "revision de precios",
    "validacion comercial",
    "precios verificados",
    "revision de valores",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La cotización coincide con el contrato y tiene vigencia.",
    ESTADO_PARCIAL: "La cotización no está plenamente acreditada.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la cotización ni su correspondencia.",
}


def _validar_precios(subrequisito, candidatos, texto):
    if contiene_frase(texto, _CORRESPONDENCIA_PRECIOS):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _CORRESPONDENCIA_PRECIOS),
            "Se identifica correspondencia de precios entre cotización y contrato.",
        )
    if contiene_frase(texto, _COTIZACION) and contiene_frase(texto, _PRECIOS):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _PRECIOS),
            "Se mencionan precios sin acreditar su correspondencia con la cotización.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó correspondencia de precios con la cotización.",
    )


def _validar_cantidades(subrequisito, candidatos, texto):
    if contiene_frase(texto, _CORRESPONDENCIA_CANTIDADES):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _CORRESPONDENCIA_CANTIDADES),
            "Se identifica correspondencia de cantidades entre cotización y contrato.",
        )
    if contiene_frase(texto, _COTIZACION) and contiene_frase(
        texto, _CANTIDADES
    ):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _CANTIDADES),
            "Se mencionan cantidades sin acreditar su correspondencia con la cotización.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó correspondencia de cantidades con la cotización.",
    )


def _validar_vigencia(subrequisito, candidatos, texto):
    if (
        contiene_frase(texto, _VIGENCIA_30)
        and contiene_frase(texto, _COTIZACION)
        and not contiene_frase(texto, ("tiempo de entrega",))
    ):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _VIGENCIA_30),
            "La cotización declara vigencia de 30 días calendario.",
        )
    if contiene_frase(texto, _COTIZACION) and contiene_frase(
        texto, _VIGENCIA
    ):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _VIGENCIA),
            "Se menciona vigencia sin precisar 30 días calendario.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó la vigencia de 30 días de la cotización.",
    )


def validar_gc06(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la cotización, su correspondencia y vigencia."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-06.1": lambda sub: _validar_precios(
            sub, candidatos.get("GC-06.1", []), texto
        ),
        "GC-06.2": lambda sub: _validar_cantidades(
            sub, candidatos.get("GC-06.2", []), texto
        ),
        "GC-06.3": lambda sub: _validar_vigencia(
            sub, candidatos.get("GC-06.3", []), texto
        ),
        "GC-06.4": lambda sub: resultado_evidencia(
            sub,
            texto,
            _VERIFICACION,
            candidatos.get("GC-06.4", []),
            cumple="Se identifica verificación de precios antes de formalizar.",
            parcial="Se menciona revisión de precios sin acreditar la verificación.",
            ausente="No se identificó verificación de precios.",
            terminos_parciales=_PRECIOS + ("revision", "validacion"),
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
