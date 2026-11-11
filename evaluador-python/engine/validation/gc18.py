"""Regla determinista para GC-18 (actualización de la relación de contratos)."""
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

_RELACION = (
    "relacion de contratos",
    "registro de contratos",
    "registrado en la relacion",
    "base de contratos",
)
_OTROSI = ("otrosi", "prorroga", "prorroga del contrato")
_ACTUALIZACION_PLAZO = (
    "actualizacion del plazo",
    "prorroga del plazo",
    "nueva duracion",
    "actualizar duracion",
    "ampliacion del plazo",
)
_FECHA_INICIO = (
    "fecha de inicio del tramite",
    "fecha de inicio",
    "fecha de radicacion",
    "fecha de solicitud",
)
_FIRMA_GERENTE = (
    "firma del gerente general",
    "firmado por el gerente general",
    "gerente general",
)
_QUINCENAL = (
    "dias 15 y 30",
    "15 y 30 de cada mes",
    "actualizacion quincenal",
    "cada 15 dias",
    "dos veces al mes",
)

_OBSERVACIONES = {
    ESTADO_CUMPLE: "La relación de contratos está registrada y actualizada.",
    ESTADO_PARCIAL: "La actualización de la relación de contratos está incompleta.",
    ESTADO_NO_IDENTIFICADO: "No se identificó la relación de contratos.",
    ESTADO_NO_APLICA: "No aplica actualización de plazo por otrosí o prórroga.",
}


def _validar_registro(subrequisito, candidatos, texto):
    if contiene_frase(texto, _RELACION):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _RELACION),
            "El contrato se registra en la relación de contratos.",
        )
    if contiene_frase(texto, ("registro", "relacion")) and contiene_frase(
        texto, ("contrato",)
    ):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, ("registro", "relacion")),
            "Se menciona registro sin precisar la relación de contratos.",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        [],
        "No se identificó el registro en la relación de contratos.",
    )


def _validar_plazo(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _OTROSI):
        return no_aplica(
            subrequisito, "No se identificó otrosí ni prórroga."
        )
    if contiene_frase(texto, _ACTUALIZACION_PLAZO):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, _ACTUALIZACION_PLAZO),
            "Se actualiza el plazo o duración por otrosí o prórroga.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        candidatos_con(candidatos, _OTROSI),
        "Se identifica otrosí o prórroga sin actualizar el plazo.",
    )


def validar_gc18(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida el registro y actualización de la relación de contratos."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-18.1": lambda sub: _validar_registro(
            sub, candidatos.get("GC-18.1", []), texto
        ),
        "GC-18.2": lambda sub: _validar_plazo(
            sub, candidatos.get("GC-18.2", []), texto
        ),
        "GC-18.3": lambda sub: resultado_evidencia(
            sub,
            texto,
            _FECHA_INICIO,
            candidatos.get("GC-18.3", []),
            cumple="Se registra la fecha de inicio del trámite.",
            parcial="Se menciona una fecha sin precisar el inicio del trámite.",
            ausente="No se identificó la fecha de inicio del trámite.",
            terminos_parciales=("fecha",),
        ),
        "GC-18.4": lambda sub: resultado_evidencia(
            sub,
            texto,
            _FIRMA_GERENTE,
            candidatos.get("GC-18.4", []),
            cumple="Se identifica la firma del gerente general.",
            parcial="Se menciona gerencia sin acreditar la firma.",
            ausente="No se identificó la firma del gerente general.",
            terminos_parciales=("gerente",),
        ),
        "GC-18.5": lambda sub: resultado_evidencia(
            sub,
            texto,
            _QUINCENAL,
            candidatos.get("GC-18.5", []),
            cumple="La relación se actualiza los días 15 y 30 de cada mes.",
            parcial="Se menciona actualización sin precisar la periodicidad.",
            ausente="No se identificó la actualización quincenal.",
            terminos_parciales=("actualizacion",),
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
