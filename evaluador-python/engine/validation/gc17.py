"""Regla determinista para GC-17 (gestión documental)."""
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

_DIGITALIZACION = (
    "digitalizacion",
    "digitalizado",
    "digitalizan",
    "digitalizar",
    "escaneado",
    "documento escaneado",
    "copia digital",
    "archivo digital",
)
_BITACORA = (
    "bitacora",
    "carpeta bitacora",
    "seccion bitacora",
    "archivado en bitacora",
    "carpeta del contrato",
)
_NOMENCLATURA = (
    "nomenclatura",
    "nombre del archivo",
    "identificacion del documento",
    "asesor, constructora y obra",
    "incluye asesor",
    "constructora y obra",
)
_FIRMADOS = ("documentos firmados", "documento firmado", "contrato firmado")

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La gestión documental cumple digitalización, archivo y nomenclatura.",
    ESTADO_PARCIAL: "La gestión documental está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la gestión documental.",
}


def validar_gc17(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida digitalización, archivo en Bitácora y nomenclatura documental."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-17.1": lambda sub: resultado_evidencia(
            sub,
            texto,
            _DIGITALIZACION,
            candidatos.get("GC-17.1", []),
            cumple="Los documentos firmados se digitalizan.",
            parcial="Se mencionan documentos firmados sin acreditar su digitalización.",
            ausente="No se identificó la digitalización de documentos firmados.",
            terminos_parciales=_FIRMADOS,
        ),
        "GC-17.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _BITACORA,
            candidatos.get("GC-17.2", []),
            cumple="Los documentos se guardan en la carpeta o sección Bitácora.",
            parcial="Se menciona archivo sin precisar la Bitácora.",
            ausente="No se identificó el archivo en Bitácora.",
            terminos_parciales=("carpeta", "archivo"),
        ),
        "GC-17.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _NOMENCLATURA,
            candidatos.get("GC-17.3", []),
            cumple="La nomenclatura incluye asesor, constructora y obra.",
            parcial="Se menciona identificación sin precisar sus componentes.",
            ausente="No se identificó la nomenclatura documental.",
            terminos_parciales=("nombre", "identificacion"),
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
