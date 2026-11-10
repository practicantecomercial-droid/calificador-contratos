"""Utilidades de texto compartidas por las capas de reconocimiento."""
from __future__ import annotations

import re
import unicodedata

_RE_TOKEN = re.compile(r"[a-z0-9]+")
_RE_ESPACIOS = re.compile(r"\s+")

_STOPWORDS = {
    "para", "como", "cuando", "donde", "sobre", "entre", "desde", "hasta",
    "debe", "deben", "estar", "esta", "este", "esto", "estos", "estas",
    "caso", "parte", "cada", "todo", "toda", "todos", "todas", "otro",
    "otra", "otros", "otras", "tiene", "tener", "sera", "seran", "con",
    "por", "los", "las", "del", "que", "una", "uno", "sus", "segun", "al",
    "el", "la", "de", "y", "o", "en", "a", "se", "su", "es", "son", "fue",
    "han", "ha", "lo", "le", "les", "mas", "pero", "sino", "tambien",
    "cual", "cuales", "quien", "quienes", "mientras", "durante", "mediante",
    "respecto", "dicho", "dicha", "dichos", "dichas", "mismo", "misma",
    "puede", "pueden", "ser", "hace", "hacer", "sido", "sea", "sean",
    "fueron", "era", "eran", "seria", "serian", "no",
}

try:  # pragma: no cover - la dependencia está en requirements
    from snowballstemmer import stemmer as _crear_stemmer

    _STEMMER = _crear_stemmer("spanish")
except Exception:  # pragma: no cover - degradación segura
    _STEMMER = None


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes y con puntuación convertida en espacios."""
    descompuesto = unicodedata.normalize("NFKD", texto or "")
    sin_tildes = "".join(c for c in descompuesto if not unicodedata.combining(c))
    limpio = re.sub(r"[^a-z0-9%]+", " ", sin_tildes.lower())
    return _RE_ESPACIOS.sub(" ", limpio).strip()


def _raiz(token: str) -> str:
    return _STEMMER.stemWord(token) if _STEMMER else token


def palabras(texto: str) -> list[str]:
    """Palabras de contenido sin stemming (para coincidencia literal)."""
    return [
        token
        for token in _RE_TOKEN.findall(normalizar(texto))
        if len(token) >= 3 and token not in _STOPWORDS
    ]


_GENERICOS_SEMANTICA = {
    "anticipo", "pago", "pagos", "valor", "total", "contrato", "contratos",
    "suministro", "entrega", "entregas", "factura", "facturas",
    "condicion", "condiciones", "plazo", "dias", "monto", "global",
    "parte", "caso", "clausula", "contratante", "contratista",
    "obligacion", "obligaciones", "documento", "documentos",
    "aprobacion", "aprobado", "aprobada", "aprobar", "estado",
}

GENERICOS_SEMANTICA_RAIZ = frozenset(_raiz(t) for t in _GENERICOS_SEMANTICA)


def tokens(texto: str) -> list[str]:
    """Tokens normalizados, sin palabras vacías y con raíz (stem) en español."""
    salida = []
    for token in _RE_TOKEN.findall(normalizar(texto)):
        if len(token) <= 2 or token in _STOPWORDS:
            continue
        salida.append(_raiz(token))
    return salida


def terminos_distintivos(texto: str) -> set[str]:
    return set(tokens(texto)) - GENERICOS_SEMANTICA_RAIZ


def comparte_distintivo(consulta: str, texto: str) -> bool:
    """True si el texto comparte al menos un término no genérico con la consulta."""
    return bool(terminos_distintivos(consulta) & set(tokens(texto)))


def alternativas(conceptos) -> list[str]:
    """Expande ``a / b / c`` en frases sueltas y descarta términos sin texto.

    Las alternativas puramente numéricas (``40%``, ``0,40``) se omiten: los
    porcentajes se validan en la fase determinista, no por coincidencia léxica.
    """
    vistos = set()
    salida = []
    for concepto in conceptos or []:
        for alternativa in re.split(r"\s*/\s*", concepto):
            alternativa = alternativa.strip(" .;,")
            clave = normalizar(alternativa)
            if not clave or clave in vistos:
                continue
            if not any(len(t) >= 3 for t in _RE_TOKEN.findall(clave)):
                continue
            vistos.add(clave)
            salida.append(alternativa)
    return salida


def consulta_semantica(subrequisito, criterio=None) -> str:
    """Construye la consulta BM25 con búsquedas sugeridas, requisito y conceptos."""
    partes = []
    if criterio:
        partes.extend(criterio.get("queries_semanticas", []))
    partes.append(subrequisito.get("texto", ""))
    conceptos = subrequisito.get("conceptos") or (criterio or {}).get("conceptos", [])
    partes.extend(alternativas(conceptos))
    return " ".join(p for p in partes if p)
