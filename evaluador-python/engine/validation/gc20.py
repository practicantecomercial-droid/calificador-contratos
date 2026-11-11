"""Regla determinista para GC-20 (firma y gestión de pólizas)."""
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

_SOLICITUD_FIRMA = (
    "solicitud de firma de polizas",
    "firma de polizas a gerencia",
    "remitir polizas a gerencia",
    "solicitar firma de polizas",
)
_POLIZAS_FIRMADAS = (
    "polizas firmadas",
    "poliza firmada",
    "firma de la poliza",
    "polizas suscritas",
)
_DIGITALIZACION = (
    "digitalizacion de polizas",
    "polizas digitalizadas",
    "digitalizadas",
    "polizas escaneadas",
    "copia digital de polizas",
)
_BITACORA = (
    "archivo en bitacora",
    "polizas en bitacora",
    "archivadas en bitacora",
)
_NOMENCLATURA = (
    "nomenclatura que identifica asesor, constructora, obra, contrato y polizas",
    "incluye asesor, constructora, obra, contrato y polizas",
    "nomenclatura de polizas",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La firma y gestión de pólizas está evidenciada.",
    ESTADO_PARCIAL: "La firma y gestión de pólizas está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la firma y gestión de pólizas.",
}


def _validar_solicitud(subrequisito, candidatos, texto):
    if contiene_frase(texto, _SOLICITUD_FIRMA):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _SOLICITUD_FIRMA),
            "Se solicita la firma de las pólizas a Gerencia.",
        )
    if contiene_frase(texto, ("poliza",)) and contiene_frase(
        texto, ("gerencia",)
    ):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, ("poliza", "gerencia")),
            "Se mencionan pólizas y Gerencia sin acreditar la solicitud de firma.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó la solicitud de firma de pólizas.",
    )


def validar_gc20(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la firma, digitalización y archivo de las pólizas."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-20.1": lambda sub: _validar_solicitud(
            sub, candidatos.get("GC-20.1", []), texto
        ),
        "GC-20.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _POLIZAS_FIRMADAS,
            candidatos.get("GC-20.2", []),
            cumple="Se evidencia la firma de las pólizas.",
            parcial="Se mencionan pólizas sin acreditar su firma.",
            ausente="No se identificaron pólizas firmadas.",
            terminos_parciales=("poliza",),
        ),
        "GC-20.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _DIGITALIZACION,
            candidatos.get("GC-20.3", []),
            cumple="Se digitalizan las pólizas firmadas.",
            parcial="Se mencionan pólizas sin acreditar su digitalización.",
            ausente="No se identificó la digitalización de las pólizas.",
            terminos_parciales=("poliza", "digital", "escane"),
        ),
        "GC-20.4": lambda sub: resultado_evidencia(
            sub,
            texto,
            _BITACORA,
            candidatos.get("GC-20.4", []),
            cumple="Las pólizas se archivan en Bitácora.",
            parcial="Se menciona Bitácora sin precisar el archivo de pólizas.",
            ausente="No se identificó el archivo de pólizas en Bitácora.",
            terminos_parciales=("bitacora",),
        ),
        "GC-20.5": lambda sub: resultado_evidencia(
            sub,
            texto,
            _NOMENCLATURA,
            candidatos.get("GC-20.5", []),
            cumple="La nomenclatura identifica asesor, constructora, obra, contrato y pólizas.",
            parcial="Se menciona nomenclatura sin precisar sus componentes.",
            ausente="No se identificó la nomenclatura de las pólizas.",
            terminos_parciales=("nomenclatura",),
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
