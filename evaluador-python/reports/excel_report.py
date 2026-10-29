"""Exporta los resultados a Excel."""
import pandas as pd

from config import REPORTS_DIR


def export_results_to_excel(resultados, summary=None, output_path=None):
    filas = []
    for r in resultados:
        filas.append({
            "ID": r["criterio_id"],
            "Criterio": r["nombre"],
            "Categoría": r.get("categoria", ""),
            "Peso": r.get("peso", 1),
            "Crítico": "Sí" if r.get("critico") else "No",
            "Estado": r["estado"].upper(),
            "Cobertura": r.get("cobertura", ""),
            "Encontrado": ", ".join(r.get("encontrados", [])),
            "Falta": ", ".join(r.get("faltantes", [])),
            "Justificación": r["justificacion"],
        })
    df = pd.DataFrame(filas)
    if output_path is None:
        output_path = REPORTS_DIR / "evaluacion.xlsx"
    df.to_excel(str(output_path), index=False)
    return str(output_path)
