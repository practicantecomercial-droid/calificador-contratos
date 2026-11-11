"""Regla determinista para GC-21 (entrega de documentos al asesor)."""
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

_ENTREGA = ("entrega fisica", "envio por correo electronico", "correo electronico")
_DOS_EJEMPLARES = (
    "contrato firmado en dos ejemplares",
    "otrosi firmado en dos ejemplares",
    "dos ejemplares firmados",
    "dos copias firmadas",
)
_POLIZAS = ("polizas firmadas", "poliza firmada", "polizas suscritas")
_CUENTA_ANTICIPO = (
    "cuenta de cobro del anticipo",
    "cuenta de cobro anticipo",
    "factura del anticipo",
)
_CARTA_ENVIO = (
    "carta de envio de documentos",
    "carta de envio",
    "carta remisoria",
    "oficio de envio",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La entrega de documentos al asesor está evidenciada.",
    ESTADO_PARCIAL: "La entrega de documentos al asesor está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la entrega de documentos al asesor.",
    ESTADO_NO_APLICA: "No aplica entrega de pólizas firmadas.",
}


def _validar_entrega(subrequisito, candidatos, texto):
    fisica = contiene_frase(texto, ("entrega fisica",))
    correo = contiene_frase(texto, ("correo electronico", "envio por correo"))
    if fisica and correo:
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _ENTREGA),
            "Se evidencia entrega física y envío por correo electrónico.",
        )
    if fisica or correo:
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _ENTREGA),
            "Solo se evidencia uno de los canales de entrega.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó la entrega física ni el envío por correo.",
    )


def _validar_polizas(subrequisito, candidatos, texto):
    if not contiene_frase(texto, ("poliza",)):
        return no_aplica(
            subrequisito, "No se identificaron pólizas aplicables."
        )
    if contiene_frase(texto, _POLIZAS):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _POLIZAS),
            "Se evidencian pólizas firmadas.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, ("poliza",)),
        "Se mencionan pólizas sin acreditar su firma.",
    )


def validar_gc21(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la entrega de documentos al asesor comercial."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-21.1": lambda sub: _validar_entrega(
            sub, candidatos.get("GC-21.1", []), texto
        ),
        "GC-21.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _DOS_EJEMPLARES,
            candidatos.get("GC-21.2", []),
            cumple="El contrato u otrosí está firmado en dos ejemplares.",
            parcial="Se mencionan dos ejemplares sin acreditar la firma.",
            ausente="No se identificó el contrato firmado en dos ejemplares.",
            terminos_parciales=("dos ejemplares", "dos copias"),
        ),
        "GC-21.3": lambda sub: _validar_polizas(
            sub, candidatos.get("GC-21.3", []), texto
        ),
        "GC-21.4": lambda sub: resultado_evidencia(
            sub,
            texto,
            _CUENTA_ANTICIPO,
            candidatos.get("GC-21.4", []),
            cumple="Se identifica la cuenta de cobro del anticipo.",
            parcial="Se menciona el anticipo sin su cuenta de cobro.",
            ausente="No se identificó la cuenta de cobro del anticipo.",
            terminos_parciales=("anticipo",),
        ),
        "GC-21.5": lambda sub: resultado_evidencia(
            sub,
            texto,
            _CARTA_ENVIO,
            candidatos.get("GC-21.5", []),
            cumple="Se identifica la carta de envío de documentos.",
            parcial="Se menciona envío sin carta remisoria.",
            ausente="No se identificó la carta de envío.",
            terminos_parciales=("carta", "envio"),
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
