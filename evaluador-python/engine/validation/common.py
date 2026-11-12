"""Utilidades compartidas por las reglas deterministas específicas."""
from __future__ import annotations

import re

from ..recognition.text import normalizar
from ..schema import (
    ALCANCE_EVIDENCIA_EXTERNA,
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
from .operators import contiene_frase


def fragmentos(texto):
    """Divide un texto en fragmentos de cláusula u observación."""
    return [
        fragmento.strip()
        for fragmento in re.split(r"\s+-\s+|\n|;", texto or "")
        if fragmento.strip()
    ]


def fragmentos_con(texto, terminos):
    return [
        fragmento
        for fragmento in fragmentos(texto)
        if contiene_frase(fragmento, terminos)
    ]


def fragmentos_con_contexto(texto, terminos, siguientes=1):
    """Fragmentos que contienen los términos, unidos con los siguientes."""
    partes = fragmentos(texto)
    bloques = []
    for indice, parte in enumerate(partes):
        if contiene_frase(parte, terminos):
            bloques.append(" ".join(partes[indice : indice + 1 + siguientes]))
    return bloques


_MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def _parse_fecha(texto):
    norm = normalizar(texto)
    coincidencia = re.search(
        r"(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})", norm
    )
    if coincidencia:
        mes = _MESES.get(coincidencia.group(2))
        if mes:
            return (
                int(coincidencia.group(3)),
                mes,
                int(coincidencia.group(1)),
            )
    coincidencia = re.search(
        r"([a-z]+)\s+(\d{1,2})\s+de\s+(\d{4})", norm
    )
    if coincidencia:
        mes = _MESES.get(coincidencia.group(1))
        if mes:
            return (
                int(coincidencia.group(3)),
                mes,
                int(coincidencia.group(2)),
            )
    return None


def _rangos_fechas(texto):
    norm = normalizar(texto)
    patron = re.compile(
        r"desde\s+(?:el\s+)?"
        r"(\d{1,2}\s+de\s+[a-z]+\s+de\s+\d{4}|[a-z]+\s+\d{1,2}\s+de\s+\d{4})"
        r"\s+hasta\s+(?:el\s+)?"
        r"(\d{1,2}\s+de\s+[a-z]+\s+de\s+\d{4}|[a-z]+\s+\d{1,2}\s+de\s+\d{4})"
    )
    rangos = []
    for coincidencia in patron.finditer(norm):
        inicio = _parse_fecha(coincidencia.group(1))
        fin = _parse_fecha(coincidencia.group(2))
        if inicio and fin:
            rangos.append((inicio, fin))
    return rangos


def vigencia_meses(texto):
    """Devuelve la vigencia máxima expresada en meses, o ``None``."""
    norm = normalizar(texto)
    anios = [
        int(valor)
        for valor in re.findall(r"(\d+)\s*(?:anos?|anios?)", norm)
    ]
    meses = [
        int(valor)
        for valor in re.findall(r"(\d+)\s*(?:mes|meses)", norm)
    ]
    valores = [anio * 12 for anio in anios] + meses
    for inicio, fin in _rangos_fechas(texto):
        duracion = (fin[0] - inicio[0]) * 12 + (fin[1] - inicio[1])
        if fin[2] < inicio[2]:
            duracion -= 1
        if duracion > 0:
            valores.append(duracion)
    return max(valores) if valores else None


def candidatos_con(candidatos, terminos):
    """Candidatos útiles cuyo texto contiene alguno de los términos."""
    return [
        candidato
        for candidato in candidatos_utiles(candidatos)
        if contiene_frase(candidato.get("texto", ""), terminos)
    ]


def resultado(
    subrequisito,
    estado,
    candidatos=None,
    observacion="",
    confianza=None,
    contradicciones=None,
):
    """Construye el resultado de un subrequisito con confianza por estado."""
    utiles = candidatos or []
    score = max((candidato.get("score", 0.0) for candidato in utiles), default=0.0)
    if confianza is None:
        if estado == ESTADO_CUMPLE:
            confianza = min(0.95, 0.6 + 0.4 * score)
        elif estado == ESTADO_NO_CUMPLE:
            confianza = 0.8
        elif estado == ESTADO_REVISION_HUMANA:
            confianza = 0.5
        elif estado == ESTADO_NO_APLICA:
            confianza = 0.9
        else:
            confianza = 0.55 if utiles else 0.0
    return resultado_subrequisito(
        subrequisito,
        estado,
        confianza,
        score,
        utiles[:2],
        observacion,
        contradicciones,
    )


def resultado_evidencia(
    subrequisito,
    texto,
    terminos,
    candidatos,
    *,
    cumple,
    parcial,
    ausente,
    terminos_parciales=(),
    estado_ausente=ESTADO_NO_IDENTIFICADO,
):
    """Resuelve un subrequisito por presencia de evidencia y señales parciales."""
    if contiene_frase(texto, terminos):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            candidatos_con(candidatos, terminos),
            cumple,
        )
    if terminos_parciales and contiene_frase(texto, terminos_parciales):
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            candidatos_con(candidatos, terminos_parciales),
            parcial,
        )
    return resultado(
        subrequisito, estado_ausente, [], ausente
    )


def no_aplica(subrequisito, observacion):
    return resultado(subrequisito, ESTADO_NO_APLICA, [], observacion)


def observacion_criterio(estado, resultados, mensajes):
    base = mensajes.get(estado, "")
    if estado in (ESTADO_PARCIAL, ESTADO_NO_CUMPLE):
        pendientes = [
            item["subrequisito_id"]
            for item in resultados
            if item["estado"] in (
                ESTADO_PARCIAL,
                ESTADO_NO_IDENTIFICADO,
                ESTADO_NO_CUMPLE,
            )
        ]
        if pendientes:
            base = (base + " " if base else "") + (
                "Pendientes: " + ", ".join(pendientes) + "."
            )
    return base


def finalizar(criterio, resultados, contexto=None, observacion="", combinar=None):
    estado = combinar(resultados) if combinar else combinar_estado(resultados)
    confianza = calcular_confianza(resultados)
    if estado == ESTADO_CUMPLE:
        confianza = max(confianza, 0.8)
    elif estado == ESTADO_NO_CUMPLE:
        confianza = max(confianza, 0.75)
    elif estado == ESTADO_NO_APLICA:
        confianza = 0.9
    return construir_resultado(
        criterio, resultados, estado, confianza, contexto, observacion=observacion
    )


def marcar_evidencia_externa(resultado, criterio):
    """Marca alcance externo y lista la evidencia pendiente cuando falta."""
    if resultado["estado"] in (ESTADO_NO_IDENTIFICADO, ESTADO_PARCIAL):
        resultado["alcance"] = ALCANCE_EVIDENCIA_EXTERNA
        for evidencia in criterio.get("evidencia_externa", []):
            if evidencia not in resultado["informacion_faltante"]:
                resultado["informacion_faltante"].append(evidencia)
        resultado["requiere_revision_humana"] = True
    return resultado
