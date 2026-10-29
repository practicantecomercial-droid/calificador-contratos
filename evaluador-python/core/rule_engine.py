"""Motor de reglas: evalúa los 25 criterios con sub-ítems, patrones y negación."""
import yaml

from config import CHECKLIST_PATH
from . import text_cleaner as tc


def load_checklist(path=None):
    p = path or CHECKLIST_PATH
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["criterios"]


def _termino_coincide(text_norm, termino):
    tn = tc.normalize_text(termino)
    if not tn:
        return False
    if tc.contains_term(text_norm, tn):
        return True
    if " " in tn:
        return False
    ts = tc.stem(tn)
    for tok in tc.tokenize(text_norm):
        if tc.stem(tok) == ts:
            return True
    if len(tn) >= 5:
        return tc.fuzzy_match(text_norm, tn)
    return False


def _evaluar_patron(patron, text):
    if not patron:
        return True
    tipo = patron.get("tipo")
    if tipo == "porcentaje":
        valores = tc.extract_percentages(text)
        valor = patron.get("valor")
        return any(abs(v - valor) < 0.5 for v in valores)
    if tipo == "plazo":
        plazos = tc.extract_durations(text)
        unidad = tc.normalize_unit(patron.get("unidad"))
        valor = patron.get("valor")
        comparacion = patron.get("comparacion", "=")
        for p in plazos:
            if p["unidad"] != unidad:
                continue
            if comparacion == ">=":
                ok = p["valor"] >= valor
            elif comparacion == "<=":
                ok = p["valor"] <= valor
            else:
                ok = p["valor"] == valor
            if ok:
                return True
        return False
    return False


def _evaluar_subitem(sub, text_norm, text):
    terminos = sub.get("terminos") or []
    patron = sub.get("patron")
    negacion = sub.get("negacion")

    encontrados = [t for t in terminos if _termino_coincide(text_norm, t)]
    patron_cumple = _evaluar_patron(patron, text)

    negado = False
    if negacion and encontrados:
        negado = any(tc.has_negation_near(text_norm, t) for t in encontrados)

    cumple = (not terminos or bool(encontrados)) and patron_cumple and (not negado)
    return cumple, encontrados


def evaluar_criterio(criterio, text_norm, text):
    subitems = criterio.get("subitems", [])
    encontrados = []
    faltantes = []
    for sub in subitems:
        cumple, _ = _evaluar_subitem(sub, text_norm, text)
        (encontrados if cumple else faltantes).append(sub["nombre"])

    total = len(subitems)
    cumplidos = len(encontrados)
    minimo = criterio.get("minimo_subitems", 1)

    if total == 0:
        estado = "no_cumple"
    elif cumplidos >= min(minimo, total):
        estado = "cumple"
    elif cumplidos > 0:
        estado = "parcial"
    else:
        estado = "no_cumple"

    if estado == "cumple":
        justificacion = f"Cumple ({cumplidos}/{total}): " + ", ".join(encontrados)
    elif estado == "parcial":
        justificacion = (
            f"Parcial ({cumplidos}/{total}). Encontrado: "
            + (", ".join(encontrados) or "—")
            + ". Falta: " + ", ".join(faltantes)
        )
    else:
        justificacion = "No cumple. Falta: " + ", ".join(faltantes)

    return {
        "criterio_id": criterio.get("id"),
        "nombre": criterio.get("nombre"),
        "categoria": criterio.get("categoria"),
        "peso": criterio.get("peso", 1),
        "critico": criterio.get("critico", False),
        "estado": estado,
        "cobertura": f"{cumplidos}/{total}",
        "cumplidos": cumplidos,
        "total": total,
        "encontrados": encontrados,
        "faltantes": faltantes,
        "justificacion": justificacion,
    }


def evaluar_checklist(texto, criterios=None):
    criterios = criterios if criterios is not None else load_checklist()
    text_norm = tc.normalize_text(texto)
    return [evaluar_criterio(c, text_norm, texto) for c in criterios]
