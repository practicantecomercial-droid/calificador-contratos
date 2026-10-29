"""Evidencias: localiza términos en el texto y devuelve fragmentos."""
from . import text_cleaner as tc


def find_evidence(text, term, radio=40):
    tn = tc.normalize_text(term)
    idx = tc.normalize_text(text).find(tn)
    if idx == -1:
        return None
    start = max(0, idx - radio)
    end = min(len(text), idx + len(term) + radio)
    return text[start:end].strip()


def find_evidence_page(pages, term):
    for p in pages:
        if tc.normalize_text(term) in tc.normalize_text(p["texto"]):
            return p["pagina"]
    return None


def build_finding(criterio, text, pages=None):
    """Añade evidencia a un resultado: para cada término encontrado, un fragmento."""
    evidencias = []
    for term in criterio.get("terminos", []):
        frag = find_evidence(text, term)
        if frag:
            pagina = find_evidence_page(pages, term) if pages else None
            evidencias.append({"termino": term, "fragmento": frag, "pagina": pagina})
    return evidencias
