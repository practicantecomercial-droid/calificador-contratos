"""Regla determinista para GC-16 (requisitos para la firma de gerencia)."""
from __future__ import annotations

from ..schema import ESTADO_CUMPLE, ESTADO_NO_IDENTIFICADO, ESTADO_PARCIAL
from .common import (
    candidatos_con,
    finalizar,
    marcar_evidencia_externa,
    resultado,
)
from .generic import combinar_estado
from .operators import contiene_frase

_DOS_COPIAS = ("dos copias", "dos ejemplares", "dos tantos")
_DOCUMENTOS = ("documentos del contrato", "documentos contractuales", "contrato")
_EVIDENCIA_VERBO = (
    "anexa",
    "anexan",
    "adjunta",
    "adjuntan",
    "presenta",
    "presentan",
    "se incluye",
    "se incluyen",
)
_FIRMA_COMERCIAL = (
    "firma previa del director comercial",
    "firmado por el director comercial",
    "firma del director comercial",
    "direccion comercial",
)
_FIRMA_GERENCIA = ("firma de gerencia", "firma del gerente general", "firma del gerente")
_COTIZACION = (
    "cotizacion firmada",
    "cotizaciones firmadas",
    "cotizacion actualizada",
    "cotizaciones actualizadas",
    "propuesta suscrita",
)
_COTIZACION_MENCION = ("cotizacion", "cotizaciones", "propuesta")


def _validar_copias(subrequisito, candidatos, texto):
    if contiene_frase(texto, _DOS_COPIAS):
        evidencia = candidatos_con(candidatos, _DOS_COPIAS)
        if contiene_frase(texto, _EVIDENCIA_VERBO) and contiene_frase(
            texto, _DOCUMENTOS
        ):
            return resultado(
                subrequisito,
                ESTADO_CUMPLE,
                evidencia,
                "Se evidencian dos copias de los documentos del contrato.",
            )
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            evidencia,
            "Se indican dos copias, pero no se evidencia su anexo.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificaron dos copias de los documentos del contrato.",
    )


def _validar_firma(subrequisito, candidatos, texto):
    if contiene_frase(texto, _FIRMA_COMERCIAL):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _FIRMA_COMERCIAL),
            "Se identifica la firma previa del director comercial.",
        )
    if contiene_frase(texto, _FIRMA_GERENCIA):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _FIRMA_GERENCIA),
            "Se menciona firma de gerencia sin evidencia de la firma del director comercial.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó la firma previa del director comercial.",
    )


def _validar_cotizaciones(subrequisito, candidatos, texto):
    if contiene_frase(texto, _COTIZACION):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _COTIZACION),
            "Se identifican cotizaciones firmadas y actualizadas.",
        )
    if contiene_frase(texto, _COTIZACION_MENCION):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _COTIZACION_MENCION),
            "Se mencionan cotizaciones sin evidencia de firma o actualización.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificaron cotizaciones firmadas y actualizadas.",
    )


def _observacion_gc16(estado, resultados):
    if estado == ESTADO_CUMPLE:
        return "Requisitos para la firma de gerencia completos."
    if estado == ESTADO_PARCIAL:
        pendientes = [
            item["subrequisito_id"]
            for item in resultados
            if item["estado"] != ESTADO_CUMPLE
        ]
        return "Requisitos de firma incompletos: " + ", ".join(pendientes) + "."
    if estado == ESTADO_NO_IDENTIFICADO:
        return "No se identificaron los documentos para la firma de gerencia."
    return "Requiere revisión humana de los requisitos de firma."


def validar_gc16(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida copias, firma del director comercial y cotizaciones."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-16.1": lambda sub: _validar_copias(
            sub, candidatos.get("GC-16.1", []), texto
        ),
        "GC-16.2": lambda sub: _validar_firma(
            sub, candidatos.get("GC-16.2", []), texto
        ),
        "GC-16.3": lambda sub: _validar_cotizaciones(
            sub, candidatos.get("GC-16.3", []), texto
        ),
    }

    resultados = [
        validadores[subrequisito_id](subrequisitos[subrequisito_id])
        for subrequisito_id in validadores
        if subrequisito_id in subrequisitos
    ]
    estado = combinar_estado(resultados)
    resultado_criterio = finalizar(
        criterio,
        resultados,
        contexto,
        observacion=_observacion_gc16(estado, resultados),
    )
    return marcar_evidencia_externa(resultado_criterio, criterio)
