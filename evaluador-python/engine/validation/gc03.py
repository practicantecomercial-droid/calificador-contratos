"""Regla determinista para GC-03 (independencia suministro e instalación)."""
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

_SUMINISTRO = ("suministro", "provision de bienes", "entrega de productos")
_INSTALACION = ("instalacion", "montaje", "puesta en obra")
_INDEPENDENCIA = (
    "servicios independientes",
    "conceptos separados",
    "por separado",
    "de manera separada",
    "independencia",
    "no incluye la instalacion",
    "no incluye instalacion",
)
_DEPENDENCIA = (
    "condicionado a la instalacion",
    "supeditado a la instalacion",
    "depende de la instalacion",
    "una vez instalado",
    "hasta tanto se instale",
)
_NO_DEPENDENCIA = (
    "no depende de la instalacion",
    "no esta condicionado a la instalacion",
    "no se supedita a la instalacion",
)
_FACTURACION = ("facturacion", "cobro", "factura")
_FACTURACION_SEPARADA = (
    "facturacion separada",
    "cobro independiente",
    "facturas separadas",
    "cobro por separado",
    "facturacion independiente",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "Suministro e instalación se reconocen como independientes.",
    ESTADO_PARCIAL: "No se acredita plenamente la independencia entre suministro e instalación.",
    ESTADO_NO_CUMPLE: "El pago del suministro está condicionado a la instalación.",
    ESTADO_NO_IDENTIFICADO: "No se identificaron condiciones de independencia.",
    ESTADO_NO_APLICA: "No aplica facturación separada en este contrato.",
}


def _validar_conceptos(subrequisito, candidatos, texto):
    if not (
        contiene_frase(texto, _SUMINISTRO)
        and contiene_frase(texto, _INSTALACION)
    ):
        return resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificaron suministro e instalación como conceptos diferenciados.",
        )
    if contiene_frase(texto, _INDEPENDENCIA):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _INDEPENDENCIA),
            "Se identifica independencia entre suministro e instalación.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _SUMINISTRO + _INSTALACION),
        "Se mencionan suministro e instalación sin acreditar su independencia.",
    )


def _validar_pago(subrequisito, candidatos, texto):
    if contiene_frase(texto, _NO_DEPENDENCIA):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _NO_DEPENDENCIA),
            "El pago del suministro no depende de la instalación.",
        )
    if contiene_frase(texto, _DEPENDENCIA):
        return resultado(
            subrequisito,
            ESTADO_NO_CUMPLE,
            candidatos_con(candidatos, _DEPENDENCIA),
            "El pago del suministro está condicionado a la instalación.",
        )
    if contiene_frase(texto, _INDEPENDENCIA):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _INDEPENDENCIA),
            "El pago del suministro no depende de la instalación.",
        )
    if (
        contiene_frase(texto, _SUMINISTRO)
        and contiene_frase(texto, _INSTALACION)
        and contiene_frase(texto, _FACTURACION)
    ):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _FACTURACION),
            "Se mencionan pagos sin precisar la independencia del suministro.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificaron condiciones de pago independientes.",
    )


def _validar_facturacion_separada(subrequisito, candidatos, texto):
    if contiene_frase(texto, _FACTURACION_SEPARADA):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _FACTURACION_SEPARADA),
            "Se identifica facturación separada por concepto.",
        )
    if (
        contiene_frase(texto, _FACTURACION)
        and contiene_frase(texto, _SUMINISTRO)
        and contiene_frase(texto, _INSTALACION)
    ):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, _FACTURACION),
            "Se menciona facturación sin precisar si es separada.",
        )
    return no_aplica(
        subrequisito, "No se identificó facturación separada aplicable."
    )


def validar_gc03(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la independencia entre suministro e instalación."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-03.1": lambda sub: _validar_conceptos(
            sub, candidatos.get("GC-03.1", []), texto
        ),
        "GC-03.2": lambda sub: _validar_pago(
            sub, candidatos.get("GC-03.2", []), texto
        ),
        "GC-03.3": lambda sub: _validar_facturacion_separada(
            sub, candidatos.get("GC-03.3", []), texto
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
