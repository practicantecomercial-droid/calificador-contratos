"""Regla determinista para GC-02 (forma de pago).

Implementa el "cómo" descrito en el markdown: anticipo del 40% sobre el valor
total, saldo del 60% contra entrega, amortización solo si hay facturaciones
parciales y crédito solo si está autorizado.
"""
from __future__ import annotations

from ..schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
)
from .generic import (
    calcular_confianza,
    candidatos_utiles,
    combinar_estado,
    construir_resultado,
    resultado_subrequisito,
)
from .operators import contiene_frase, contiene_porcentaje, porcentajes

_ANTICIPO = (
    "anticipo",
    "pago inicial",
    "abono inicial",
    "desembolso inicial",
)
_SALDO = ("saldo", "remanente", "valor restante")
_BASE_VALOR = (
    "valor total",
    "valor global",
    "monto total",
    "valor del contrato",
    "valor contrato",
)
_ENTREGA = (
    "contra entrega",
    "al entregar",
    "una vez recibido",
    "recibido el suministro",
    "entrega del suministro",
)
_AMORTIZACION = (
    "amortizar",
    "amortizacion",
    "descontar",
    "descuento del anticipo",
    "aplicar proporcionalmente",
    "amortizacion proporcional",
)
_TRIGGER_PARCIALES = (
    "facturacion parcial",
    "facturaciones parciales",
    "facturas parciales",
    "entregas parciales",
    "actas parciales",
    "pagos parciales",
    "cortes parciales",
)
_TRIGGER_CREDITO = (
    "credito",
    "plazo de pago",
    "credito comercial",
)
_AUTORIZACION = (
    "aprobacion de credito",
    "credito aprobado",
    "aprobacion expresa",
    "previa autorizacion",
    "cupo autorizado",
    "requisitos de cartera",
    "autorizacion del area",
    "autorizado por",
)


def _candidatos_con(candidatos, terminos):
    return [
        candidato
        for candidato in candidatos_utiles(candidatos)
        if contiene_frase(candidato.get("texto", ""), terminos)
    ]


def _tiene_excepcion(candidatos) -> bool:
    return any(
        candidato.get("contexto", {}).get("excepcion")
        or candidato.get("contexto", {}).get("condicional")
        for candidato in candidatos
    )


def _resultado(subrequisito, estado, candidatos, observacion, confianza=None):
    utiles = candidatos or []
    score = max((candidato.get("score", 0.0) for candidato in utiles), default=0.0)
    if confianza is None:
        if estado == ESTADO_CUMPLE:
            confianza = min(0.95, 0.6 + 0.4 * score)
        elif estado == ESTADO_NO_CUMPLE:
            confianza = 0.8
        elif estado == ESTADO_PARCIAL:
            confianza = 0.55
        elif estado == ESTADO_REVISION_HUMANA:
            confianza = 0.5
        elif estado == ESTADO_NO_APLICA:
            confianza = 0.9
        else:
            confianza = 0.0
    return resultado_subrequisito(
        subrequisito, estado, confianza, score, utiles[:2], observacion
    )


def _validar_anticipo(subrequisito, candidatos):
    clausulas = _candidatos_con(candidatos, _ANTICIPO)
    if not clausulas:
        return _resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificó cláusula de anticipo.",
        )

    con_porcentaje = [
        candidato
        for candidato in clausulas
        if contiene_porcentaje(candidato["texto"], 40)
    ]
    con_base = [
        candidato
        for candidato in con_porcentaje
        if contiene_frase(candidato["texto"], _BASE_VALOR)
    ]
    if con_base:
        return _resultado(
            subrequisito,
            ESTADO_CUMPLE,
            con_base,
            "Anticipo del 40% calculado sobre el valor total del contrato.",
        )
    if con_porcentaje:
        return _resultado(
            subrequisito,
            ESTADO_PARCIAL,
            con_porcentaje,
            "Anticipo del 40% sin base de cálculo explícita.",
        )

    if any(porcentajes(candidato["texto"]) for candidato in clausulas):
        estado = (
            ESTADO_REVISION_HUMANA
            if _tiene_excepcion(clausulas)
            else ESTADO_NO_CUMPLE
        )
        observacion = (
            "El anticipo no equivale al 40% del valor total."
            if estado == ESTADO_NO_CUMPLE
            else "El anticipo difiere del 40% y tiene una condición documentada."
        )
        return _resultado(subrequisito, estado, clausulas, observacion)
    return _resultado(
        subrequisito,
        ESTADO_PARCIAL,
        clausulas,
        "Se menciona anticipo pero no se establece el porcentaje.",
    )


def _validar_saldo(subrequisito, candidatos):
    clausulas = _candidatos_con(candidatos, _SALDO)
    if not clausulas:
        return _resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificó cláusula de saldo.",
        )

    con_60 = [
        candidato
        for candidato in clausulas
        if contiene_porcentaje(candidato["texto"], 60)
    ]
    con_entrega = _candidatos_con(candidatos, _ENTREGA)
    if con_60 and con_entrega:
        evidencia = con_60[:1] + [c for c in con_entrega if c not in con_60][:1]
        return _resultado(
            subrequisito,
            ESTADO_CUMPLE,
            evidencia,
            "Saldo del 60% facturado contra entrega del suministro.",
        )
    if con_60:
        return _resultado(
            subrequisito,
            ESTADO_PARCIAL,
            con_60,
            "Saldo del 60% sin condición de entrega explícita.",
        )
    if con_entrega:
        return _resultado(
            subrequisito,
            ESTADO_PARCIAL,
            con_entrega,
            "Pago contra entrega sin saldo del 60% explícito.",
        )

    if any(porcentajes(candidato["texto"]) for candidato in clausulas):
        return _resultado(
            subrequisito,
            ESTADO_NO_CUMPLE,
            clausulas,
            "El saldo no equivale al 60% del valor total.",
        )
    return _resultado(
        subrequisito,
        ESTADO_PARCIAL,
        clausulas,
        "Se menciona saldo pero no se establece el porcentaje.",
    )


def _validar_amortizacion(subrequisito, candidatos, texto_documento):
    if not contiene_frase(texto_documento, _TRIGGER_PARCIALES):
        return _resultado(
            subrequisito,
            ESTADO_NO_APLICA,
            [],
            "El contrato no contempla facturaciones parciales.",
        )

    clausulas = _candidatos_con(candidatos, _AMORTIZACION)
    if clausulas or contiene_frase(texto_documento, _AMORTIZACION):
        return _resultado(
            subrequisito,
            ESTADO_CUMPLE,
            clausulas,
            "El contrato define la amortización proporcional del anticipo.",
        )
    return _resultado(
        subrequisito,
        ESTADO_PARCIAL,
        [],
        "Hay facturaciones parciales pero no se indica cómo amortizar el anticipo.",
    )


def _validar_credito(subrequisito, candidatos, texto_documento):
    if not contiene_frase(texto_documento, _TRIGGER_CREDITO):
        return _resultado(
            subrequisito,
            ESTADO_NO_APLICA,
            [],
            "El contrato no contempla crédito.",
        )

    autorizacion = _candidatos_con(candidatos, _AUTORIZACION)
    if autorizacion or contiene_frase(texto_documento, _AUTORIZACION):
        return _resultado(
            subrequisito,
            ESTADO_CUMPLE,
            autorizacion,
            "El crédito está respaldado por una autorización.",
        )
    return _resultado(
        subrequisito,
        ESTADO_REVISION_HUMANA,
        _candidatos_con(candidatos, _TRIGGER_CREDITO),
        "Se menciona crédito sin evidencia de aprobación.",
    )


def _combinar_gc02(resultados):
    estado = combinar_estado(resultados)
    if estado == ESTADO_CUMPLE:
        esenciales = [
            resultado
            for resultado in resultados
            if resultado["subrequisito_id"] in ("GC-02.1", "GC-02.2")
        ]
        if any(resultado["estado"] != ESTADO_CUMPLE for resultado in esenciales):
            return ESTADO_PARCIAL
    return estado


def _observacion_gc02(estado, resultados, contexto):
    if estado == ESTADO_CUMPLE:
        return "Forma de pago con anticipo del 40% y saldo del 60% contra entrega."
    if estado == ESTADO_NO_CUMPLE:
        incumplidos = [
            resultado["subrequisito_id"]
            for resultado in resultados
            if resultado["estado"] == ESTADO_NO_CUMPLE
        ]
        return "Forma de pago no cumple: " + ", ".join(incumplidos) + "."
    if estado == ESTADO_PARCIAL:
        pendientes = [
            resultado["subrequisito_id"]
            for resultado in resultados
            if resultado["estado"] in (ESTADO_NO_IDENTIFICADO, ESTADO_PARCIAL)
        ]
        return "Forma de pago incompleta: " + ", ".join(pendientes) + "."
    if estado == ESTADO_REVISION_HUMANA:
        return "Forma de pago requiere revisión humana por condiciones especiales."
    if estado == ESTADO_NO_APLICA:
        return "No aplica para este contrato."
    observacion = "No se identificó una forma de pago con anticipo del 40% y saldo del 60% contra entrega."
    if contexto and contexto.get("forma_pago", {}).get("vacia"):
        observacion += " La forma de pago del contrato está vacía."
    return observacion


def validar_gc02(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida GC-02 combinando sus cuatro subrequisitos atómicos."""
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    resultados = []
    if "GC-02.1" in subrequisitos:
        resultados.append(
            _validar_anticipo(
                subrequisitos["GC-02.1"], candidatos.get("GC-02.1", [])
            )
        )
    if "GC-02.2" in subrequisitos:
        resultados.append(
            _validar_saldo(subrequisitos["GC-02.2"], candidatos.get("GC-02.2", []))
        )
    if "GC-02.3" in subrequisitos:
        resultados.append(
            _validar_amortizacion(
                subrequisitos["GC-02.3"],
                candidatos.get("GC-02.3", []),
                texto_documento,
            )
        )
    if "GC-02.4" in subrequisitos:
        resultados.append(
            _validar_credito(
                subrequisitos["GC-02.4"],
                candidatos.get("GC-02.4", []),
                texto_documento,
            )
        )

    estado = _combinar_gc02(resultados)
    confianza = calcular_confianza(resultados)
    if estado == ESTADO_CUMPLE:
        confianza = max(confianza, 0.8)
    elif estado == ESTADO_NO_CUMPLE:
        confianza = max(confianza, 0.75)
    elif estado == ESTADO_NO_APLICA:
        confianza = 0.9

    return construir_resultado(
        criterio,
        resultados,
        estado,
        confianza,
        contexto,
        observacion=_observacion_gc02(estado, resultados, contexto),
    )
