"""Regla determinista para GC-19 (solicitud de anticipo y pólizas)."""
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

_CORREO = (
    "correo al analista de cartera",
    "analista de cartera y jefe administrativo",
    "correo enviado",
    "solicitud por correo",
    "envio de correo",
)
_CUENTA_ANTICIPO = (
    "cuenta de cobro del anticipo",
    "solicitud de cuenta de cobro",
    "cuenta de cobro anticipo",
    "factura del anticipo",
)
_POLIZAS = (
    "solicitud de polizas",
    "polizas requeridas",
    "solicitar polizas",
    "emision de polizas",
)
_ASEGURADORA = (
    "aseguradora",
    "compania aseguradora",
    "aseguradoras especificas",
)
_BITACORA = (
    "archivar en bitacora",
    "bitacora junto con el contrato",
    "documentacion en bitacora",
    "archivo en bitacora",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La solicitud de anticipo y pólizas está evidenciada.",
    ESTADO_PARCIAL: "La solicitud de anticipo y pólizas está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la solicitud de anticipo y pólizas.",
    ESTADO_NO_APLICA: "No aplica mención de aseguradoras específicas.",
}


def _validar_aseguradora(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _ASEGURADORA):
        return no_aplica(
            subrequisito, "El contrato no determina aseguradoras específicas."
        )
    if contiene_frase(texto, ("solicitud", "mencion", "indicar")):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _ASEGURADORA),
            "La solicitud menciona las aseguradoras específicas.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _ASEGURADORA),
        "Se mencionan aseguradoras sin acreditar su inclusión en la solicitud.",
    )


def validar_gc19(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la solicitud de anticipo, pólizas y su archivo en Bitácora."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-19.1": lambda sub: resultado_evidencia(
            sub,
            texto,
            _CORREO,
            candidatos.get("GC-19.1", []),
            cumple="Se evidencia el correo al analista de cartera y jefe administrativo.",
            parcial="Se mencionan los destinatarios sin acreditar el correo.",
            ausente="No se identificó el correo de solicitud.",
            terminos_parciales=("analista de cartera", "jefe administrativo"),
        ),
        "GC-19.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _CUENTA_ANTICIPO,
            candidatos.get("GC-19.2", []),
            cumple="Se solicita la cuenta de cobro del anticipo.",
            parcial="Se menciona el anticipo sin solicitar la cuenta de cobro.",
            ausente="No se identificó la solicitud de cuenta de cobro.",
            terminos_parciales=("anticipo",),
        ),
        "GC-19.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _POLIZAS,
            candidatos.get("GC-19.3", []),
            cumple="Se solicitan las pólizas requeridas.",
            parcial="Se mencionan pólizas sin acreditar su solicitud.",
            ausente="No se identificó la solicitud de pólizas.",
            terminos_parciales=("poliza",),
        ),
        "GC-19.4": lambda sub: _validar_aseguradora(
            sub, candidatos.get("GC-19.4", []), texto
        ),
        "GC-19.5": lambda sub: resultado_evidencia(
            sub,
            texto,
            _BITACORA,
            candidatos.get("GC-19.5", []),
            cumple="La documentación se archiva en Bitácora junto con el contrato.",
            parcial="Se menciona Bitácora sin precisar el archivo conjunto.",
            ausente="No se identificó el archivo en Bitácora.",
            terminos_parciales=("bitacora",),
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
