"""Cálculo de puntajes ponderados y controles críticos."""

FACTOR = {"cumple": 1.0, "parcial": 0.5, "no_cumple": 0.0}


def calculate_score(resultados):
    total_peso = sum(r.get("peso", 1) for r in resultados)
    if total_peso == 0:
        return 0.0
    puntos = sum(r.get("peso", 1) * FACTOR.get(r["estado"], 0.0) for r in resultados)
    return round(puntos / total_peso * 100, 1)


def category_scores(resultados):
    grupos = {}
    for r in resultados:
        grupos.setdefault(r.get("categoria", "otra"), {"peso": 0, "puntos": 0.0, "criterios": 0})
        g = grupos[r.get("categoria", "otra")]
        g["peso"] += r.get("peso", 1)
        g["puntos"] += r.get("peso", 1) * FACTOR.get(r["estado"], 0.0)
        g["criterios"] += 1
    out = {}
    for cat, g in grupos.items():
        out[cat] = {
            "criterios": g["criterios"],
            "porcentaje": round(g["puntos"] / g["peso"] * 100, 1) if g["peso"] else 0.0,
        }
    return out


def check_critical_failures(resultados):
    return [r for r in resultados if r.get("critico") and r["estado"] == "no_cumple"]


def build_summary(resultados):
    estados = {"cumple": 0, "parcial": 0, "no_cumple": 0}
    for r in resultados:
        estados[r["estado"]] += 1
    criticos = check_critical_failures(resultados)
    apto = len(criticos) == 0
    return {
        "puntaje": calculate_score(resultados),
        "estados": estados,
        "criticos_fallidos": [c["nombre"] for c in criticos],
        "apto": apto,
        "categorias": category_scores(resultados),
    }
