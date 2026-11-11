"""Regla determinista para GC-04 (facturación del suministro)."""
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

_FACTURACION = (
    "facturacion",
    "facturar",
    "emitir factura",
    "radicar factura",
    "cobrar",
)
_SUMINISTRO = (
    "suministro",
    "productos",
    "materiales",
    "elementos entregados",
)
_ENTREGA_OBRA = (
    "entrega en obra",
    "entrega del suministro",
    "recibido en obra",
    "recepcion en obra",
    "entrega en el proyecto",
)
_ENTREGA_PARCIAL = (
    "entrega parcial",
    "entregas parciales",
    "despachos parciales",
    "entregas por lotes",
    "entrega total",
    "pedido completo",
    "totalidad del pedido",
    "segun lo acordado",
    "conforme al cronograma",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La facturación del suministro está ligada a la entrega.",
    ESTADO_PARCIAL: "La facturación del suministro no está plenamente precisada.",
    ESTADO_NO_IDENTIFICADO: "No se identificaron condiciones de facturación del suministro.",
}


def _validar_entrega(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _FACTURACION):
        return resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificó la facturación del suministro.",
        )
    if contiene_frase(texto, _SUMINISTRO) and contiene_frase(
        texto, _ENTREGA_OBRA
    ):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _FACTURACION + _ENTREGA_OBRA),
            "La facturación del suministro se vincula a la entrega en obra.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _FACTURACION + _SUMINISTRO),
        "Se menciona facturación del suministro sin precisar la entrega en obra.",
    )


def validar_gc04(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la facturación del suministro y su vínculo con la entrega."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-04.1": lambda sub: _validar_entrega(
            sub, candidatos.get("GC-04.1", []), texto
        ),
        "GC-04.2": lambda sub: resultado_evidencia(
            sub,
            texto,
            _ENTREGA_PARCIAL,
            candidatos.get("GC-04.2", []),
            cumple="Se identifican entregas parciales o totales según lo acordado.",
            parcial="Se menciona la entrega del suministro sin precisar su modalidad.",
            ausente="No se identificó la modalidad de entrega del suministro.",
            terminos_parciales=_SUMINISTRO + ("entrega",),
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
