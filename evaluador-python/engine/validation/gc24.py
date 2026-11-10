"""Regla determinista para GC-24 (validación de anticipo y pedido)."""
from __future__ import annotations

from ..schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
)
from .common import (
    candidatos_con,
    finalizar,
    marcar_evidencia_externa,
    resultado,
)
from .generic import combinar_estado
from .operators import contiene_frase

_VALIDACION_PAGO = (
    "anticipo pagado",
    "abono recibido",
    "pago inicial confirmado",
    "validacion de pago",
    "comprobante",
    "consignacion",
    "transferencia",
)
_PEDIDO = (
    "generacion de pedido",
    "creacion de orden",
    "liberacion del pedido",
    "pedido",
)
_FABRICACION = ("fabricacion", "produccion", "enviar a planta")
_BLOQUEO = (
    "bloqueo",
    "retencion del pedido",
    "hasta confirmar",
    "hasta el pago",
    "no puede enviarse",
    "no se enviara",
)
_ASESOR = (
    "asesor comercial",
    "gestion del anticipo",
    "gestionar el anticipo",
    "solicitar el anticipo",
)
_EXCEPCION = ("excepcion", "excepciones")
_AUTORIZACION = (
    "autorizacion administrativa",
    "aprobacion comercial",
    "jefe administrativo",
    "director comercial",
    "validacion del jefe",
)


def _validar_anticipo(subrequisito, candidatos, texto):
    pago = contiene_frase(texto, _VALIDACION_PAGO)
    pedido = contiene_frase(texto, _PEDIDO)
    evidencia = candidatos_con(candidatos, _VALIDACION_PAGO + _PEDIDO)
    if pago and pedido:
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            evidencia,
            "Se valida el anticipo antes de generar el pedido.",
        )
    if pago or pedido:
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            evidencia,
            "Se menciona solo una parte del control de anticipo y pedido.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó la validación del anticipo antes del pedido.",
    )


def _validar_fabricacion(subrequisito, candidatos, texto):
    if not (contiene_frase(texto, _FABRICACION) and contiene_frase(texto, _PEDIDO)):
        return resultado(
            subrequisito,
            ESTADO_NO_APLICA,
            [],
            "El contrato no describe generación de pedido y fabricación.",
        )
    evidencia = candidatos_con(candidatos, _BLOQUEO)
    if contiene_frase(texto, _BLOQUEO):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            evidencia,
            "Se bloquea el envío a fabricación hasta confirmar el abono.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        evidencia,
        "No se identifica el bloqueo de fabricación hasta confirmar el abono.",
    )


def _validar_asesor(subrequisito, candidatos, texto):
    if contiene_frase(texto, _ASESOR):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _ASESOR),
            "La gestión del anticipo se solicita al asesor comercial.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó la gestión del anticipo por el asesor comercial.",
    )


def _validar_excepcion(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _EXCEPCION):
        return resultado(
            subrequisito,
            ESTADO_NO_APLICA,
            [],
            "No se registran excepciones al control del anticipo.",
        )
    evidencia = candidatos_con(candidatos, _EXCEPCION)
    if contiene_frase(texto, _AUTORIZACION):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            evidencia,
            "La excepción cuenta con validación del responsable.",
        )
    return resultado(
        subrequisito,
        ESTADO_REVISION_HUMANA,
        evidencia,
        "Hay una excepción sin evidencia de validación.",
    )


def _observacion_gc24(estado, resultados):
    if estado == ESTADO_CUMPLE:
        return "Validación de anticipo y control de pedido completos."
    if estado == ESTADO_PARCIAL:
        pendientes = [
            item["subrequisito_id"]
            for item in resultados
            if item["estado"] != ESTADO_CUMPLE
        ]
        return "Control de anticipo incompleto: " + ", ".join(pendientes) + "."
    if estado == ESTADO_NO_IDENTIFICADO:
        return "No se identificó la validación del anticipo ni el control del pedido."
    if estado == ESTADO_NO_APLICA:
        return "No aplica para este contrato."
    return "Requiere revisión humana del control de anticipo."


def validar_gc24(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida el control de anticipo, pedido, fabricación y excepciones."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-24.1": lambda sub: _validar_anticipo(
            sub, candidatos.get("GC-24.1", []), texto
        ),
        "GC-24.2": lambda sub: _validar_fabricacion(
            sub, candidatos.get("GC-24.2", []), texto
        ),
        "GC-24.3": lambda sub: _validar_asesor(
            sub, candidatos.get("GC-24.3", []), texto
        ),
        "GC-24.4": lambda sub: _validar_excepcion(
            sub, candidatos.get("GC-24.4", []), texto
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
        observacion=_observacion_gc24(estado, resultados),
    )
    return marcar_evidencia_externa(resultado_criterio, criterio)
