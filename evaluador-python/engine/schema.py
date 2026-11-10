"""Constantes y constructores del motor de reconocimiento.

Los modelos son diccionarios planos para mantener el estilo del proyecto
(dicts + YAML, sin dependencias de validación adicionales).
"""
from __future__ import annotations

from datetime import datetime, timezone

VERSION_KB = "1.0"

ESTADO_CUMPLE = "CUMPLE"
ESTADO_NO_CUMPLE = "NO CUMPLE"
ESTADO_PARCIAL = "PARCIAL"
ESTADO_NO_IDENTIFICADO = "NO IDENTIFICADO"
ESTADO_NO_APLICA = "NO APLICA"
ESTADO_REVISION_HUMANA = "REVISIÓN HUMANA"

ESTADOS = (
    ESTADO_CUMPLE,
    ESTADO_NO_CUMPLE,
    ESTADO_PARCIAL,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_NO_APLICA,
    ESTADO_REVISION_HUMANA,
)

ALCANCE_DOCUMENTAL = "DOCUMENTAL"
ALCANCE_EXPEDIENTE = "EXPEDIENTE"
ALCANCE_EVIDENCIA_EXTERNA = "EVIDENCIA EXTERNA PENDIENTE"

ALCANCES = (ALCANCE_DOCUMENTAL, ALCANCE_EXPEDIENTE, ALCANCE_EVIDENCIA_EXTERNA)

UMBRALES = {
    "alta": 0.85,
    "probable": 0.70,
    "debil": 0.50,
}

MARCADORES_CONTRADICCION = {
    "negacion": ("no se reconocerá", "no estará obligado", "no aplica", "no"),
    "exclusividad": ("únicamente", "exclusivamente", "solo"),
    "condicion": ("siempre que", "cuando", "en caso de", "sujeto a"),
    "excepcion": ("salvo", "excepto", "a menos que"),
    "aprobacion": ("previa autorización", "con aprobación expresa", "por escrito"),
    "temporalidad": ("antes de", "después de", "al momento de", "dentro de", "a partir de"),
}


def nuevo_subrequisito(
    *,
    criterio_id,
    indice,
    texto,
    conceptos=None,
    regla_texto="",
    operador=None,
    esencial=True,
    condicional=False,
):
    """Crea un subrequisito atómico derivado de una condición de validación."""
    return {
        "id": f"{criterio_id}.{indice}",
        "criterio_id": criterio_id,
        "indice": indice,
        "texto": texto,
        "conceptos": list(conceptos or []),
        "regla_texto": regla_texto,
        "operador": operador,
        "esencial": bool(esencial),
        "condicional": bool(condicional),
    }


def nuevo_criterio(
    *,
    criterio_id,
    numero,
    nombre,
    obligacion="",
    objetivo="",
    categoria="",
    conceptos=None,
    subrequisitos=None,
    reglas_decision=None,
    queries_semanticas=None,
    requiere_evidencia_externa=False,
    evidencia_externa=None,
    peso=1,
    critico=False,
    minimo_subitems=None,
    nombre_legacy="",
):
    """Crea un criterio con su estructura completa y metadatos de compatibilidad."""
    return {
        "criterio_id": criterio_id,
        "numero": numero,
        "nombre": nombre,
        "nombre_legacy": nombre_legacy,
        "categoria": categoria,
        "obligacion": obligacion,
        "objetivo": objetivo,
        "conceptos": list(conceptos or []),
        "subrequisitos": list(subrequisitos or []),
        "reglas_decision": list(reglas_decision or []),
        "queries_semanticas": list(queries_semanticas or []),
        "requiere_evidencia_externa": bool(requiere_evidencia_externa),
        "evidencia_externa": list(evidencia_externa or []),
        "peso": peso,
        "critico": bool(critico),
        "minimo_subitems": minimo_subitems,
    }


def nuevo_resultado(
    *,
    criterio_id,
    criterio,
    estado,
    confianza=0.0,
    evidencia=None,
    condiciones_verificadas=None,
    observacion="",
    numero=None,
    alcance=ALCANCE_DOCUMENTAL,
    subrequisitos=None,
    informacion_faltante=None,
    contradicciones=None,
    requiere_revision_humana=False,
    fecha_analisis=None,
    version_kb=VERSION_KB,
):
    """Crea el resultado auditable de un criterio (formato §1.4 + extensiones)."""
    if estado not in ESTADOS:
        raise ValueError(f"Estado no válido: {estado!r}")
    return {
        "criterio_id": criterio_id,
        "criterio": criterio,
        "numero": numero,
        "estado": estado,
        "confianza": round(float(confianza), 2),
        "alcance": alcance,
        "evidencia": list(evidencia or []),
        "condiciones_verificadas": dict(condiciones_verificadas or {}),
        "subrequisitos": list(subrequisitos or []),
        "informacion_faltante": list(informacion_faltante or []),
        "contradicciones": list(contradicciones or []),
        "requiere_revision_humana": bool(requiere_revision_humana),
        "observacion": observacion,
        "fecha_analisis": fecha_analisis or datetime.now(timezone.utc).isoformat(),
        "version_kb": version_kb,
    }
