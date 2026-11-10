"""Parser de la base de conocimiento (instructivo de gestión de contratos).

El Markdown es la fuente de verdad: no se modifica. El parser extrae, por cada
criterio ``GC-XX``, su requisito, objetivo, conceptos, condiciones atómicas,
reglas de decisión y consultas semánticas.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .schema import VERSION_KB, nuevo_criterio, nuevo_subrequisito

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_KNOWLEDGE_PATH = (
    BASE_DIR / "knowledge" / "Criterios_Gestion_Contratos_Interdoors.md"
)

ETIQUETAS = {
    "requisito": "Requisito fuente",
    "objetivo": "Objetivo de reconocimiento",
    "conceptos": "Conceptos y expresiones relacionadas",
    "condiciones": "Condiciones de validación",
    "reglas": "Reglas de decisión",
    "queries": "Búsqueda semántica sugerida",
}

_CRITERIO_RE = re.compile(r"^##\s+(GC-\d{2})\.\s+(.+?)\s*$", re.MULTILINE)
_SECCION_RE = re.compile(r"^#\s+\S", re.MULTILINE)
_LABEL_RE = re.compile(r"\*\*(?P<label>[^*\n]+?):\*\*")
_QUERY_RE = re.compile(r"`([^`]+)`")
_CONDICIONAL_RE = re.compile(
    r"\b(si|cuando|según corresponda|segun corresponda|cuando corresponda|"
    r"cuando aplique|condicional|solo puede|únicamente|unicamente)\b",
    re.IGNORECASE,
)
_TABLA_RUIDO_RE = re.compile(r"^[-|=\s]+$")
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_NUM_RE = re.compile(r"\d+")

_TOKENS_GENERICOS = {
    "valor", "total", "contrato", "pago", "suministro", "entrega",
    "entregas", "factura", "facturas", "condicion", "condiciones",
    "plazo", "dias", "monto", "global", "parte", "caso",
}

_STOPWORDS = {
    "para", "como", "cuando", "donde", "sobre", "entre", "desde", "hasta",
    "debe", "deben", "estar", "esta", "este", "esto", "estos", "estas",
    "caso", "parte", "cada", "todo", "toda", "todos", "todas", "otro",
    "otra", "otros", "otras", "tiene", "tener", "sera", "serán", "sera",
    "con", "por", "los", "las", "del", "que", "una", "uno", "sus", "segun",
}


def _sin_tildes(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def _compactar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.replace("\r\n", "\n")).strip()


def _limpiar_item(texto: str) -> str:
    texto = texto.strip()
    texto = re.sub(r"^[-•]\s*", "", texto)
    texto = re.sub(r"[\s.;]+$", "", texto)
    return texto.strip()


def _lista(chunk: str):
    """Convierte un bloque de viñetas (posiblemente inline) en una lista."""
    texto = _compactar(chunk)
    if texto.startswith("- "):
        texto = texto[2:]
    partes = re.split(r"\s+-\s+", texto)
    items = [_limpiar_item(p) for p in partes]
    return [i for i in items if i]


def _queries(chunk: str):
    return [q.strip() for q in _QUERY_RE.findall(chunk) if q.strip()]


def _tokens(texto: str):
    normal = _sin_tildes(texto.lower())
    return {
        t for t in _TOKEN_RE.findall(normal)
        if len(t) > 3 and t not in _STOPWORDS
    }


def _numeros(texto: str):
    return set(_NUM_RE.findall(texto))


def _conceptos_relacionados(item: str, conceptos):
    tokens_item = _tokens(item)
    numeros_item = _numeros(item)
    relacionados = []
    for concepto in conceptos:
        compartidos = tokens_item & _tokens(concepto)
        if numeros_item & _numeros(concepto):
            relacionados.append(concepto)
            continue
        if len(compartidos) >= 2:
            relacionados.append(concepto)
            continue
        if len(compartidos) == 1:
            (token,) = compartidos
            if token not in _TOKENS_GENERICOS:
                relacionados.append(concepto)
    return relacionados


def _campos(bloque: str):
    matches = list(_LABEL_RE.finditer(bloque))
    campos = {}
    for i, match in enumerate(matches):
        inicio = match.end()
        fin = matches[i + 1].start() if i + 1 < len(matches) else len(bloque)
        campos[match.group("label").strip()] = bloque[inicio:fin]
    return campos


def _secciones_criterios(texto: str):
    matches = list(_CRITERIO_RE.finditer(texto))
    for i, match in enumerate(matches):
        inicio = match.end()
        siguiente_criterio = matches[i + 1].start() if i + 1 < len(matches) else len(texto)
        seccion = _SECCION_RE.search(texto, inicio)
        fin = min(siguiente_criterio, seccion.start()) if seccion else siguiente_criterio
        yield match.group(1), match.group(2).strip(), texto[inicio:fin]


def _limpiar_tabla(texto: str) -> str:
    lineas = []
    for linea in texto.splitlines():
        limpia = linea.strip()
        if not limpia or _TABLA_RUIDO_RE.match(limpia):
            continue
        lineas.append(limpia.strip("|").strip())
    return _compactar(" ".join(lineas))


def _parsear_externos(texto: str):
    cabecera = re.search(
        r"^#\s*3\..*?$", texto, re.MULTILINE
    )
    if not cabecera:
        return {}
    inicio = cabecera.end()
    siguiente = re.search(r"^#\s*4\..*?$", texto[inicio:], re.MULTILINE)
    fin = inicio + siguiente.start() if siguiente else len(texto)
    seccion = texto[inicio:fin]

    externos = {}
    matches = list(re.finditer(r"(GC-\d{2})", seccion))
    for i, match in enumerate(matches):
        criterio_id = match.group(1)
        desde = match.end()
        hasta = matches[i + 1].start() if i + 1 < len(matches) else len(seccion)
        descripcion = _limpiar_tabla(seccion[desde:hasta])
        externos[criterio_id] = [descripcion] if descripcion else []
    return externos


def _parsear_fuente(texto: str) -> str:
    match = re.search(r"\*\*Fuente:\*\*(.+?)\*\*Versión", texto, re.DOTALL)
    return _compactar(match.group(1)) if match else ""


def _parsear_version(texto: str) -> str:
    match = re.search(r"\*\*Versión de esta base:\*\*\s*([\d.]+)", texto)
    return match.group(1) if match else VERSION_KB


def _construir_criterio(criterio_id, nombre, bloque, externos):
    campos = _campos(bloque)
    conceptos = _lista(campos.get(ETIQUETAS["conceptos"], ""))
    condiciones = _lista(campos.get(ETIQUETAS["condiciones"], ""))

    subrequisitos = []
    for indice, condicion in enumerate(condiciones, start=1):
        condicional = bool(_CONDICIONAL_RE.search(condicion))
        subrequisitos.append(
            nuevo_subrequisito(
                criterio_id=criterio_id,
                indice=indice,
                texto=condicion,
                conceptos=_conceptos_relacionados(condicion, conceptos),
                condicional=condicional,
                esencial=not condicional,
            )
        )

    return nuevo_criterio(
        criterio_id=criterio_id,
        numero=int(criterio_id.split("-")[1]),
        nombre=nombre,
        obligacion=_compactar(campos.get(ETIQUETAS["requisito"], "")),
        objetivo=_compactar(campos.get(ETIQUETAS["objetivo"], "")),
        conceptos=conceptos,
        subrequisitos=subrequisitos,
        reglas_decision=_lista(campos.get(ETIQUETAS["reglas"], "")),
        queries_semanticas=_queries(campos.get(ETIQUETAS["queries"], "")),
        requiere_evidencia_externa=criterio_id in externos,
        evidencia_externa=externos.get(criterio_id, []),
    )


def cargar_base_conocimiento(ruta=None):
    """Carga y parsea el Markdown de criterios."""
    path = Path(ruta) if ruta else DEFAULT_KNOWLEDGE_PATH
    texto = path.read_text(encoding="utf-8")
    externos = _parsear_externos(texto)
    criterios = [
        _construir_criterio(criterio_id, nombre, bloque, externos)
        for criterio_id, nombre, bloque in _secciones_criterios(texto)
    ]
    return {
        "version": _parsear_version(texto),
        "fuente": _parsear_fuente(texto),
        "ruta": str(path),
        "criterios": criterios,
        "requieren_evidencia_externa": sorted(externos),
    }


def criterio_por_id(base, criterio_id):
    for criterio in base["criterios"]:
        if criterio["criterio_id"] == criterio_id:
            return criterio
    raise KeyError(f"Criterio no encontrado: {criterio_id}")


def criterio_por_numero(base, numero):
    for criterio in base["criterios"]:
        if criterio["numero"] == numero:
            return criterio
    raise KeyError(f"Criterio no encontrado: {numero}")


def resumen(base):
    """Resumen útil para pruebas y diagnósticos."""
    return {
        "version": base["version"],
        "total_criterios": len(base["criterios"]),
        "total_subrequisitos": sum(
            len(c["subrequisitos"]) for c in base["criterios"]
        ),
        "requieren_evidencia_externa": list(base["requieren_evidencia_externa"]),
    }
