"""Reconocimiento de evidencia por capas: literal, léxica, semántica y contextual.

Las capas solo proponen candidatos con puntaje; la decisión del estado queda en
la fase de validación.
"""
from __future__ import annotations

from ..segmenter import segmentar
from . import contextual, lexical, literal, semantic
from .text import alternativas, comparte_distintivo, consulta_semantica, normalizar, tokens

__all__ = [
    "alternativas",
    "consulta_semantica",
    "normalizar",
    "tokens",
    "reconocer_subrequisito",
    "reconocer_criterio",
    "reconocer_documento",
]


def _candidato(subrequisito, unidad, capa, termino, score_base):
    return {
        "criterio_id": subrequisito["criterio_id"],
        "subrequisito_id": subrequisito["id"],
        "unidad_id": unidad["id"],
        "tipo_unidad": unidad["tipo"],
        "texto": unidad["texto"],
        "pagina": unidad.get("pagina"),
        "lineas": list(unidad.get("lineas", [])),
        "capa": capa,
        "termino": termino,
        "score_base": round(float(score_base), 3),
        "score": round(float(score_base), 3),
        "contexto": {},
        "contradicciones": [],
        "descartable_para_concepto": False,
    }


def _espera_anticipo(subrequisito) -> bool:
    texto = normalizar(subrequisito.get("texto", ""))
    return "anticipo" in texto and "retencion" not in texto


def _fusionar(candidatos):
    por_unidad = {}
    for candidato in candidatos:
        actual = por_unidad.get(candidato["unidad_id"])
        if actual is None:
            por_unidad[candidato["unidad_id"]] = dict(
                candidato, capas=[candidato["capa"]]
            )
            continue
        actual["capas"].append(candidato["capa"])
        if candidato["score"] > actual["score"]:
            capas = actual["capas"]
            actual.update(candidato)
            actual["capas"] = capas
    for candidato in por_unidad.values():
        candidato["capas"] = sorted(set(candidato["capas"]))
    return list(por_unidad.values())


def reconocer_subrequisito(
    subrequisito,
    unidades,
    *,
    criterio=None,
    indice=None,
    usar_semantica=True,
    usar_llm=False,
    top_k=3,
    umbral_lexico=0.5,
    umbral_semantico=0.15,
):
    """Devuelve candidatos de evidencia ordenados para un subrequisito."""
    if not unidades:
        return []

    conceptos = subrequisito.get("conceptos") or (criterio or {}).get("conceptos", [])
    terminos = alternativas(conceptos)
    if not terminos:
        terminos = [subrequisito.get("texto", "")]

    candidatos = []
    for unidad in unidades:
        coincidencias = literal.buscar(unidad["texto"], terminos)
        if coincidencias:
            mejor = coincidencias[0]
            candidatos.append(_candidato(
                subrequisito, unidad, "literal", mejor["termino"], mejor["score"]
            ))

        score_lexico, termino_lexico = lexical.puntuar(unidad["texto"], terminos)
        if score_lexico >= umbral_lexico:
            candidatos.append(_candidato(
                subrequisito, unidad, "lexico", termino_lexico, score_lexico
            ))

    consulta = consulta_semantica(subrequisito, criterio)
    if usar_semantica:
        if indice is None:
            indice = semantic.IndiceBM25([unidad["texto"] for unidad in unidades])
        for posicion, score in indice.mejores(
            consulta, top_k=top_k, umbral=umbral_semantico
        ):
            unidad = unidades[posicion]
            if not comparte_distintivo(consulta, unidad["texto"]):
                continue
            candidatos.append(_candidato(
                subrequisito, unidad, "semantico", consulta, score
            ))

    espera_anticipo = _espera_anticipo(subrequisito)
    for candidato in candidatos:
        analisis = contextual.analizar(
            candidato["texto"], candidato["termino"], subrequisito
        )
        candidato["contexto"] = analisis["flags"]
        candidato["contradicciones"] = analisis["contradicciones"]
        candidato["score"] = round(candidato["score_base"] * analisis["ajuste"], 3)
        candidato["descartable_para_concepto"] = bool(
            (
                analisis["flags"]["es_retencion"]
                or analisis["flags"]["es_garantia_anticipo"]
            )
            and espera_anticipo
        )

    fusionados = _fusionar(candidatos)
    fusionados.sort(
        key=lambda candidato: (
            -candidato["score"],
            candidato["pagina"] or 0,
            candidato["lineas"][0] if candidato["lineas"] else 0,
        )
    )

    if usar_llm:
        fusionados = semantic.reordenar_con_llm(consulta, fusionados)
    return fusionados


def reconocer_criterio(
    criterio,
    unidades,
    *,
    indice=None,
    usar_semantica=True,
    usar_llm=False,
    top_k=3,
):
    """Reconoce todos los subrequisitos de un criterio."""
    if usar_semantica and indice is None:
        indice = semantic.IndiceBM25([unidad["texto"] for unidad in unidades])

    por_subrequisito = {}
    mejores = {}
    for subrequisito in criterio.get("subrequisitos", []):
        candidatos = reconocer_subrequisito(
            subrequisito,
            unidades,
            criterio=criterio,
            indice=indice,
            usar_semantica=usar_semantica,
            usar_llm=usar_llm,
            top_k=top_k,
        )
        por_subrequisito[subrequisito["id"]] = candidatos
        mejores[subrequisito["id"]] = candidatos[0] if candidatos else None

    return {
        "criterio_id": criterio.get("criterio_id"),
        "subrequisitos": por_subrequisito,
        "mejores": mejores,
    }


def reconocer_documento(
    base,
    documento,
    *,
    criterios=None,
    usar_semantica=True,
    usar_llm=False,
    top_k=3,
):
    """Segmenta el documento y reconoce los criterios solicitados."""
    unidades = segmentar(documento)
    indice = (
        semantic.IndiceBM25([unidad["texto"] for unidad in unidades])
        if usar_semantica
        else None
    )
    seleccionados = (
        set(criterios)
        if criterios is not None
        else {criterio["criterio_id"] for criterio in base.get("criterios", [])}
    )
    resultados = {}
    for criterio in base.get("criterios", []):
        if criterio["criterio_id"] not in seleccionados:
            continue
        resultados[criterio["criterio_id"]] = reconocer_criterio(
            criterio,
            unidades,
            indice=indice,
            usar_semantica=usar_semantica,
            usar_llm=usar_llm,
            top_k=top_k,
        )
    return {"unidades": unidades, "criterios": resultados}
