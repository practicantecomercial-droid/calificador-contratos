"""Orquestador end-to-end del motor documental.

Une lectura, contexto, reconocimiento y validación para producir un reporte
auditable de los 25 criterios. No decide por fuera de las reglas: solo compone
las fases y resume sus resultados.
"""
from __future__ import annotations

from .context import construir_contexto
from .document_reader import leer_documento
from .gc_mapping import fusionar_metadatos
from .knowledge_base import cargar_base_conocimiento
from .recognition import reconocer_documento
from .schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
    ESTADOS,
    VERSION_KB,
)
from .validation import validar_documento

FACTOR_ESTADO = {
    ESTADO_CUMPLE: 1.0,
    ESTADO_PARCIAL: 0.5,
    ESTADO_NO_CUMPLE: 0.0,
    ESTADO_NO_IDENTIFICADO: 0.0,
    ESTADO_REVISION_HUMANA: 0.5,
    ESTADO_NO_APLICA: None,
}


def _preparar_base(base, metadatos):
    base = base if base is not None else cargar_base_conocimiento()
    if metadatos:
        fusionar_metadatos(base)
    return base


def _resumen_documento(documento):
    paginas = documento.get("paginas", [])
    return {
        "ruta": documento.get("ruta"),
        "formato": documento.get("formato"),
        "paginas": len(paginas),
        "caracteres": len(documento.get("texto", "")),
        "ocr": any(pagina.get("ocr") for pagina in paginas),
        "campos": len(documento.get("campos", {})),
        "campos_vacios": list(documento.get("campos_vacios", [])),
    }


def _enriquecer(resultado, criterio):
    resultado["peso"] = criterio.get("peso", 1)
    resultado["critico"] = bool(criterio.get("critico", False))
    resultado["categoria"] = criterio.get("categoria", "")
    resultado["requiere_evidencia_externa"] = bool(
        criterio.get("requiere_evidencia_externa", False)
    )
    return resultado


def _puntaje(resultados):
    peso_total = 0
    puntos = 0.0
    for resultado in resultados:
        factor = FACTOR_ESTADO[resultado["estado"]]
        if factor is None:
            continue
        peso = resultado.get("peso", 1) or 0
        peso_total += peso
        puntos += peso * factor
    return round(puntos / peso_total * 100, 1) if peso_total else 0.0


def _por_categoria(resultados):
    grupos = {}
    for resultado in resultados:
        categoria = resultado.get("categoria") or "sin categoria"
        grupo = grupos.setdefault(
            categoria, {"criterios": 0, "peso": 0, "puntos": 0.0}
        )
        grupo["criterios"] += 1
        factor = FACTOR_ESTADO[resultado["estado"]]
        if factor is None:
            continue
        peso = resultado.get("peso", 1) or 0
        grupo["peso"] += peso
        grupo["puntos"] += peso * factor

    return {
        categoria: {
            "criterios": grupo["criterios"],
            "puntaje": (
                round(grupo["puntos"] / grupo["peso"] * 100, 1)
                if grupo["peso"]
                else None
            ),
        }
        for categoria, grupo in grupos.items()
    }


def _resumen(base, resultados):
    conteo = {estado: 0 for estado in ESTADOS}
    for resultado in resultados:
        conteo[resultado["estado"]] += 1

    criticos = [resultado for resultado in resultados if resultado.get("critico")]
    criticos_no_cumplidos = [
        resultado["criterio_id"]
        for resultado in criticos
        if resultado["estado"] == ESTADO_NO_CUMPLE
    ]
    criticos_sin_evidencia = [
        resultado["criterio_id"]
        for resultado in criticos
        if resultado["estado"] == ESTADO_NO_IDENTIFICADO
    ]
    criticos_en_revision = [
        resultado["criterio_id"]
        for resultado in criticos
        if resultado["estado"] == ESTADO_REVISION_HUMANA
    ]
    confianzas = [resultado["confianza"] for resultado in resultados]

    return {
        "total_criterios": len(resultados),
        "conteo_estados": conteo,
        "puntaje": _puntaje(resultados),
        "confianza_promedio": (
            round(sum(confianzas) / len(confianzas), 2) if confianzas else 0.0
        ),
        "requieren_revision": sum(
            1 for resultado in resultados if resultado["requiere_revision_humana"]
        ),
        "criticos_no_cumplidos": criticos_no_cumplidos,
        "criticos_sin_evidencia": criticos_sin_evidencia,
        "criticos_en_revision": criticos_en_revision,
        "evidencia_externa_pendiente": list(
            base.get("requieren_evidencia_externa", [])
        ),
        "apto": not (criticos_no_cumplidos or criticos_sin_evidencia),
        "por_categoria": _por_categoria(resultados),
    }


def _advertencias(contexto, documento):
    advertencias = list(contexto.get("advertencias", []))
    if not documento.get("texto", "").strip():
        advertencias.append("El documento no contiene texto extraíble.")
    if contexto.get("valor") is None:
        advertencias.append("No se identificó el valor del contrato.")
    if contexto.get("forma_pago", {}).get("vacia"):
        advertencias.append("Forma de pago vacía en el contrato.")
    return advertencias


def evaluar_documento(
    documento,
    *,
    base=None,
    contexto=None,
    criterios=None,
    usar_semantica=True,
    usar_llm=False,
    metadatos=True,
):
    """Evalúa un documento y devuelve el reporte completo de criterios.

    ``criterios`` acepta identificadores ``GC-XX`` para limitar el análisis.
    ``metadatos`` fusiona peso, criticidad y categoría del checklist histórico.
    """
    base = _preparar_base(base, metadatos)
    contexto = contexto if contexto is not None else construir_contexto(documento)

    reconocimiento = reconocer_documento(
        base,
        documento,
        criterios=criterios,
        usar_semantica=usar_semantica,
        usar_llm=usar_llm,
    )
    validacion = validar_documento(
        base,
        reconocimiento,
        contexto=contexto,
        documento=documento,
        criterios=criterios,
    )

    resultados_por_id = validacion["criterios"]
    resultados = [
        _enriquecer(resultados_por_id[criterio["criterio_id"]], criterio)
        for criterio in base["criterios"]
        if criterio["criterio_id"] in resultados_por_id
    ]

    return {
        "version_kb": base.get("version", VERSION_KB),
        "fuente_kb": base.get("fuente", ""),
        "documento": _resumen_documento(documento),
        "contexto": contexto,
        "criterios": resultados,
        "resultados": {
            resultado["criterio_id"]: resultado for resultado in resultados
        },
        "resumen": _resumen(base, resultados),
        "advertencias": _advertencias(contexto, documento),
        "unidades": len(reconocimiento.get("unidades", [])),
    }


def evaluar_archivo(ruta, **kwargs):
    """Lee un PDF/Word/imagen y ejecuta el pipeline completo."""
    return evaluar_documento(leer_documento(ruta), **kwargs)
