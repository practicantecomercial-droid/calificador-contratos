"""Regla determinista para GC-14 (términos y condiciones de garantía)."""
from __future__ import annotations

from ..schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
)
from .common import candidatos_con, finalizar, resultado, vigencia_meses
from .generic import combinar_estado
from .operators import contiene_frase

_GARANTIA = ("garantia", "respaldo", "garantia de producto")
_PRODUCTO = ("puertas", "muebles", "carpinteria", "productos suministrados")
_ANEXO = (
    "anexo",
    "documento adjunto",
    "condiciones de garantia",
    "terminos y condiciones",
)
_ALCANCE = ("alcance", "cobertura", "exclusiones", "ampara", "cubre")
_VIGENCIA = (
    "vigencia",
    "duracion",
    "periodo de garantia",
    "desde",
    "hasta",
)
_RECLAMO = (
    "reclamacion",
    "solicitud de garantia",
    "tramite",
    "procedimiento",
    "defectos",
)


def _validar_documento(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _GARANTIA):
        return resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificó cláusula o documento de garantía.",
        )

    evidencia = candidatos_con(candidatos, _GARANTIA)
    identificado = contiene_frase(texto, _ANEXO) or contiene_frase(
        texto, ("garantia de producto",)
    )
    if not identificado:
        identificado = contiene_frase(texto, _PRODUCTO) and any(
            contiene_frase(texto, terminos)
            for terminos in (_ALCANCE, _VIGENCIA, _RECLAMO)
        )
    if identificado:
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            evidencia,
            "Se identifica el documento o cláusula de garantía de los productos.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        evidencia,
        "Se menciona garantía, pero no se identifica el documento o cláusula aplicable.",
    )


def _validar_condicion(subrequisito, candidatos, texto, terminos, descripcion):
    if not contiene_frase(texto, _GARANTIA):
        return resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificó cláusula o documento de garantía.",
        )
    evidencia = candidatos_con(candidatos, terminos)
    if contiene_frase(texto, terminos):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            evidencia,
            f"La garantía especifica {descripcion}.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        evidencia,
        f"La garantía no especifica {descripcion}.",
    )


def _validar_vigencia(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _GARANTIA):
        return resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificó cláusula o documento de garantía.",
        )
    evidencia = candidatos_con(candidatos, _VIGENCIA)
    if not contiene_frase(texto, _VIGENCIA):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            evidencia,
            "La garantía no especifica vigencia.",
        )
    meses = vigencia_meses(texto)
    if meses is None:
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            evidencia,
            "La garantía menciona vigencia pero no una duración concreta.",
        )
    return resultado(
        subrequisito,
        ESTADO_CUMPLE,
        evidencia,
        f"La garantía especifica una vigencia de {meses} meses.",
    )


def _observacion_gc14(estado, resultados):
    if estado == ESTADO_CUMPLE:
        return "Términos y condiciones de garantía completos."
    if estado == ESTADO_PARCIAL:
        pendientes = [
            item["subrequisito_id"]
            for item in resultados
            if item["estado"] != ESTADO_CUMPLE
        ]
        return "Garantía incompleta: " + ", ".join(pendientes) + "."
    if estado == ESTADO_NO_IDENTIFICADO:
        return "No se identificaron términos y condiciones de garantía."
    return "Requiere revisión humana de los términos de garantía."


def validar_gc14(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida alcance, vigencia y procedimiento de la garantía de producto."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-14.1": lambda sub: _validar_documento(
            sub, candidatos.get("GC-14.1", []), texto
        ),
        "GC-14.2": lambda sub: _validar_condicion(
            sub,
            candidatos.get("GC-14.2", []),
            texto,
            _ALCANCE,
            "alcance o cobertura",
        ),
        "GC-14.3": lambda sub: _validar_vigencia(
            sub, candidatos.get("GC-14.3", []), texto
        ),
        "GC-14.4": lambda sub: _validar_condicion(
            sub,
            candidatos.get("GC-14.4", []),
            texto,
            _RECLAMO,
            "el procedimiento de reclamación",
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
        observacion=_observacion_gc14(estado, resultados),
    )

    if estado == ESTADO_PARCIAL and contiene_frase(texto, _ANEXO):
        faltante = "Anexo de condiciones de garantía no adjunto"
        if faltante not in resultado_criterio["informacion_faltante"]:
            resultado_criterio["informacion_faltante"].append(faltante)
        resultado_criterio["requiere_revision_humana"] = True
    return resultado_criterio
