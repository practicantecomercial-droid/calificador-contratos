"""Normalización de texto, números, fechas y coincidencia de términos."""
import re
import unicodedata
from snowballstemmer import stemmer

_stemmer = stemmer("spanish")


def normalize_text(s):
    s = (s or "").lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s


def tokenize(s):
    return [t for t in re.split(r"[^a-z0-9ñ%]+", normalize_text(s)) if t]


def stem(word):
    w = normalize_text(word)
    try:
        return _stemmer.stemWord(w)
    except Exception:
        return w


NUMEROS = {
    "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11,
    "doce": 12, "trece": 13, "catorce": 14, "quince": 15, "dieciseis": 16,
    "diecisiete": 17, "dieciocho": 18, "diecinueve": 19, "veinte": 20,
    "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60,
    "setenta": 70, "ochenta": 80, "noventa": 90, "cien": 100, "ciento": 100,
}

_UNIDADES = {
    "dia": "dias", "días": "dias", "dias": "dias",
    "mes": "meses", "meses": "meses",
    "año": "años", "años": "años", "ano": "años", "anos": "años",
    "anio": "años", "anios": "años",
}


def normalize_unit(u):
    return _UNIDADES.get(normalize_text(u), normalize_text(u))


def extract_percentages(text):
    t = normalize_text(text)
    found = []
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*%", t):
        found.append(float(m.group(1).replace(",", ".")))
    num_words = "|".join(NUMEROS.keys())
    for m in re.finditer(rf"({num_words})\s+por\s+ciento", t):
        found.append(NUMEROS[m.group(1)])
    return found


def extract_durations(text):
    t = normalize_text(text)
    found = []
    unidad = r"(dias|día|meses|mes|años|anos|anios|año|anio)"
    for m in re.finditer(rf"(\d+)\s*{unidad}", t):
        found.append({"valor": int(m.group(1)), "unidad": normalize_unit(m.group(2))})
    num_words = "|".join(NUMEROS.keys())
    for m in re.finditer(rf"({num_words})\s*(?:\(\s*\d+\s*\)\s*)?{unidad}", t):
        found.append({"valor": NUMEROS[m.group(1)], "unidad": normalize_unit(m.group(2))})
    return found


def _levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


def contains_term(text_norm, term):
    return normalize_text(term) in text_norm


def fuzzy_match(text_norm, term):
    tn = normalize_text(term)
    if len(tn) < 5:
        return False
    for p in tokenize(text_norm):
        if abs(len(p) - len(tn)) > 2:
            continue
        d = _levenshtein(p, tn)
        if d <= 1 or d / max(len(tn), 1) <= 0.2:
            return True
    return False


NEGACIONES = [
    "no", "sin", "exento", "exenta", "excluido", "excluida",
    "unilateral", "excepto", "salvo", "no aplica",
]


def has_negation_near(text_norm, term, radio=6):
    tn = normalize_text(term)
    idx = text_norm.find(tn)
    if idx == -1:
        return False
    ventana = text_norm[max(0, idx - 80): idx + 80]
    tokens = ventana.split()
    for neg in NEGACIONES:
        if " " in neg:
            if neg in ventana:
                return True
        elif neg in tokens:
            return True
    return False
