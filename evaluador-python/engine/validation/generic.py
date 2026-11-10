"""Validador genérico para criterios sin regla específica."""
from __future__ import annotations

from ..schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
    nuevo_resultado,
)
from .operators import clasificar_score


def candidatos_utiles(candidatos):
    return [
        candidato
        for candidato in candidatos or []
        if not candidato.get("descartable_para_concepto")
    ]


def mejor_candidato(candidatos):
    utiles = candidatos_utiles(candidatos)
    return utiles[0] if utiles else None


def evidencia_de(candidato, subrequisito_id):
    return {
        "subrequisito_id": subrequisito_id,
        "unidad_id": candidato.get("unidad_id"),
        "tipo_unidad": candidato.get("tipo_unidad"),
        "texto": candidato.get("texto", ""),
        "pagina": candidato.get("pagina"),
        "lineas": list(candidato.get("lineas", [])),
        "capa": candidato.get("capa"),
        "termino": candidato.get("termino"),
        "score": candidato.get("score", 0.0),
    }


def _contradicciones(candidatos):
    return sorted({
        tipo
        for candidato in candidatos
        for tipo in candidato.get("contradicciones", [])
    })


def resultado_subrequisito(
    subrequisito,
    estado,
    confianza,
    score,
    candidatos,
    observacion,
    contradicciones=None,
):
    return {
        "subrequisito_id": subrequisito["id"],
        "texto": subrequisito["texto"],
        "estado": estado,
        "confianza": round(float(confianza), 2),
        "score": round(float(score), 3),
        "evidencia": [
            evidencia_de(candidato, subrequisito["id"])
            for candidato in candidatos
        ],
        "observacion": observacion,
        "contradicciones": (
            list(contradicciones)
            if contradicciones is not None
            else _contradicciones(candidatos)
        ),
    }


def estado_por_candidatos(candidatos):
    utiles = candidatos_utiles(candidatos)
    if not utiles:
        return ESTADO_NO_IDENTIFICADO
    mejor = utiles[0]
    if mejor.get("contradicciones"):
        return ESTADO_REVISION_HUMANA
    if mejor.get("capa") == "literal" and mejor.get("score", 0.0) >= 0.85:
        return ESTADO_CUMPLE
    if mejor.get("score", 0.0) >= 0.50:
        return ESTADO_REVISION_HUMANA
    return ESTADO_NO_IDENTIFICADO


def validar_subrequisito_generico(subrequisito, candidatos):
    utiles = candidatos_utiles(candidatos)
    if not utiles:
        return resultado_subrequisito(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            0.0,
            0.0,
            [],
            "Sin evidencia documental.",
        )
    mejor = utiles[0]
    estado = estado_por_candidatos(utiles)
    score = mejor.get("score", 0.0)
    if estado == ESTADO_CUMPLE:
        confianza = min(0.95, 0.5 + 0.5 * score)
    elif estado == ESTADO_REVISION_HUMANA:
        confianza = min(0.8, 0.3 + 0.4 * score)
    else:
        confianza = 0.0
    return resultado_subrequisito(
        subrequisito,
        estado,
        confianza,
        score,
        utiles[:3],
        f"Mejor coincidencia ({clasificar_score(score)}): "
        f"{mejor.get('texto', '')[:160]}",
    )


def combinar_estado(resultados):
    estados = [resultado["estado"] for resultado in resultados]
    if not estados:
        return ESTADO_NO_IDENTIFICADO
    if ESTADO_NO_CUMPLE in estados:
        return ESTADO_NO_CUMPLE
    aplicables = [estado for estado in estados if estado != ESTADO_NO_APLICA]
    if aplicables and all(estado == ESTADO_NO_IDENTIFICADO for estado in aplicables):
        return ESTADO_NO_IDENTIFICADO
    if all(estado == ESTADO_NO_APLICA for estado in estados):
        return ESTADO_NO_APLICA
    if any(estado in (ESTADO_NO_IDENTIFICADO, ESTADO_PARCIAL) for estado in estados):
        return ESTADO_PARCIAL
    if any(estado == ESTADO_REVISION_HUMANA for estado in estados):
        return ESTADO_REVISION_HUMANA
    if all(estado in (ESTADO_CUMPLE, ESTADO_NO_APLICA) for estado in estados):
        return ESTADO_CUMPLE
    return ESTADO_REVISION_HUMANA


def calcular_confianza(resultados):
    relevantes = [
        resultado
        for resultado in resultados
        if resultado["estado"] != ESTADO_NO_APLICA
    ]
    if not relevantes:
        return 0.9
    if all(resultado["estado"] == ESTADO_NO_IDENTIFICADO for resultado in relevantes):
        return 0.0
    cumplidos = sum(
        1 for resultado in relevantes if resultado["estado"] == ESTADO_CUMPLE
    )
    cobertura = cumplidos / len(relevantes)
    con_evidencia = [
        resultado["score"] for resultado in relevantes if resultado["evidencia"]
    ]
    promedio = sum(con_evidencia) / len(con_evidencia) if con_evidencia else 0.0
    penalizacion = 0.15 * sum(
        1 for resultado in resultados if resultado["contradicciones"]
    )
    confianza = 0.5 * cobertura + 0.5 * promedio - penalizacion
    return round(max(0.0, min(1.0, confianza)), 2)


def observacion_generica(estado, resultados):
    if estado == ESTADO_CUMPLE:
        return "Requisito cumplido con evidencia verificable."
    if estado == ESTADO_NO_CUMPLE:
        incumplidos = [
            resultado["subrequisito_id"]
            for resultado in resultados
            if resultado["estado"] == ESTADO_NO_CUMPLE
        ]
        return "Requisito no cumplido: " + ", ".join(incumplidos) + "."
    if estado == ESTADO_PARCIAL:
        return "Cumplimiento parcial; faltan condiciones esenciales."
    if estado == ESTADO_NO_IDENTIFICADO:
        return "No se identificó evidencia suficiente."
    if estado == ESTADO_REVISION_HUMANA:
        return "Requiere revisión humana por ambigüedad o contradicción."
    if estado == ESTADO_NO_APLICA:
        return "No aplica para este contrato."
    return ""


def construir_resultado(
    criterio,
    resultados,
    estado,
    confianza,
    contexto=None,
    observacion="",
):
    evidencia = [
        item for resultado in resultados for item in resultado["evidencia"]
    ]
    faltantes = [
        resultado["texto"]
        for resultado in resultados
        if resultado["estado"] == ESTADO_NO_IDENTIFICADO
    ]
    contradicciones = [
        {
            "subrequisito_id": resultado["subrequisito_id"],
            "tipo": tipo,
            "texto": resultado["texto"],
        }
        for resultado in resultados
        for tipo in resultado["contradicciones"]
    ]
    forma_pago_vacia = bool(
        contexto and contexto.get("forma_pago", {}).get("vacia")
    )
    if forma_pago_vacia:
        faltantes.append("Forma de pago vacía en el contrato")

    requiere_revision = (
        estado in (ESTADO_REVISION_HUMANA, ESTADO_PARCIAL)
        or bool(contradicciones)
        or (estado == ESTADO_NO_IDENTIFICADO and forma_pago_vacia)
    )

    return nuevo_resultado(
        criterio_id=criterio["criterio_id"],
        criterio=criterio["nombre"],
        numero=criterio["numero"],
        estado=estado,
        confianza=confianza,
        evidencia=evidencia,
        condiciones_verificadas={
            resultado["subrequisito_id"]: {
                "estado": resultado["estado"],
                "confianza": resultado["confianza"],
                "score": resultado["score"],
            }
            for resultado in resultados
        },
        subrequisitos=[
            {
                "subrequisito_id": resultado["subrequisito_id"],
                "texto": resultado["texto"],
                "estado": resultado["estado"],
                "confianza": resultado["confianza"],
                "score": resultado["score"],
                "evidencia": resultado["evidencia"],
                "observacion": resultado["observacion"],
                "contradicciones": resultado["contradicciones"],
            }
            for resultado in resultados
        ],
        informacion_faltante=faltantes,
        contradicciones=contradicciones,
        requiere_revision_humana=requiere_revision,
        observacion=observacion or observacion_generica(estado, resultados),
    )


def validar_criterio_generico(
    criterio,
    reconocimiento,
    contexto=None,
    texto_documento="",
):
    resultados = [
        validar_subrequisito_generico(
            subrequisito,
            reconocimiento.get("subrequisitos", {}).get(subrequisito["id"], []),
        )
        for subrequisito in criterio.get("subrequisitos", [])
    ]
    estado = combinar_estado(resultados)
    confianza = calcular_confianza(resultados)
    if estado == ESTADO_CUMPLE:
        confianza = max(confianza, 0.8)
    elif estado == ESTADO_NO_CUMPLE:
        confianza = max(confianza, 0.75)
    elif estado == ESTADO_NO_APLICA:
        confianza = 0.9
    return construir_resultado(criterio, resultados, estado, confianza, contexto)
