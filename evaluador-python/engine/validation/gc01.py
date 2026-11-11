"""Regla determinista para GC-01 (documentos del asesor comercial)."""
from __future__ import annotations

from ..schema import (
    ESTADO_CUMPLE,
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

_DOS_COPIAS = ("dos copias", "dos ejemplares", "2 copias", "dos tantos")
_CONTRATO = ("contrato",)
_EVIDENCIA_VERBO = (
    "se anexan",
    "se adjuntan",
    "se entregan",
    "se remiten",
    "anexa",
    "adjunta",
)
_COTIZACION_FIRMADA = (
    "cotizacion firmada",
    "cotizacion actualizada",
    "cotizacion vigente",
    "propuesta firmada",
    "oferta firmada",
)
_COTIZACION = ("cotizacion", "propuesta economica", "oferta")
_COSTEO = ("costeo", "desglose de costos", "analisis de costos")
_MANUAL = ("manual del contratista", "manual de contratistas")
_SST = (
    "sst",
    "seguridad y salud en el trabajo",
    "seguridad industrial",
    "arl",
)
_ANEXOS = ("anexo", "documentos adicionales", "otros requisitos")
_COORDINADOR_SST = ("coordinador sst", "firma del coordinador sst", "firma sst")
_CONSTRUCTORA = ("constructora", "constructor")
_CARTA = (
    "carta de no siniestro",
    "no siniestro",
    "certificacion de no siniestro",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "Documentos del asesor comercial completos.",
    ESTADO_PARCIAL: "Documentos del asesor comercial incompletos.",
    ESTADO_NO_IDENTIFICADO: "No se identificaron los documentos del asesor.",
}


def _validar_copias(subrequisito, candidatos, texto):
    if contiene_frase(texto, _DOS_COPIAS) and contiene_frase(texto, _CONTRATO):
        evidencia = candidatos_con(candidatos, _DOS_COPIAS)
        if contiene_frase(texto, _EVIDENCIA_VERBO):
            return resultado(
                subrequisito,
                ESTADO_CUMPLE,
                evidencia,
                "Se evidencian dos copias del contrato.",
            )
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            evidencia,
            "Se exigen dos copias, pero no se evidencia su entrega.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificaron dos copias del contrato.",
    )


def _validar_anexos(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _ANEXOS):
        return no_aplica(subrequisito, "El contrato no menciona anexos adicionales.")
    if contiene_frase(texto, _COORDINADOR_SST):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _COORDINADOR_SST),
            "Se identifica la firma del coordinador SST.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _ANEXOS),
        "Se mencionan anexos sin evidencia de la firma del coordinador SST.",
    )


def _validar_carta(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _CONSTRUCTORA):
        return no_aplica(
            subrequisito, "El cliente no se identifica como constructora."
        )
    if contiene_frase(texto, _CARTA):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _CARTA),
            "Se identifica la carta de no siniestro.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _CONSTRUCTORA),
        "El cliente es constructora y no se identificó la carta de no siniestro.",
    )


def validar_gc01(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida los documentos que debe enviar el asesor comercial."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-01.1": lambda sub: _validar_copias(
            sub, candidatos.get("GC-01.1", []), texto
        ),
        "GC-01.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _COTIZACION_FIRMADA,
            candidatos.get("GC-01.2", []),
            cumple="Se identifica la cotización firmada y actualizada.",
            parcial="Se menciona la cotización sin evidencia de firma o vigencia.",
            ausente="No se identificó la cotización firmada y actualizada.",
            terminos_parciales=_COTIZACION,
        ),
        "GC-01.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _COSTEO,
            candidatos.get("GC-01.3", []),
            cumple="Se identifica el costeo o desglose de costos.",
            parcial="",
            ausente="No se identificó el costeo o desglose de costos.",
        ),
        "GC-01.4": lambda sub: resultado_evidencia(
            sub,
            texto,
            _MANUAL,
            candidatos.get("GC-01.4", []),
            cumple="Se identifica el manual del contratista.",
            parcial="",
            ausente="No se identificó el manual del contratista.",
        ),
        "GC-01.5": lambda sub: resultado_evidencia(
            sub,
            texto,
            _SST,
            candidatos.get("GC-01.5", []),
            cumple="Se identifica la documentación de SST.",
            parcial="",
            ausente="No se identificó la documentación de SST.",
        ),
        "GC-01.6": lambda sub: _validar_anexos(
            sub, candidatos.get("GC-01.6", []), texto
        ),
        "GC-01.7": lambda sub: _validar_carta(
            sub, candidatos.get("GC-01.7", []), texto
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
