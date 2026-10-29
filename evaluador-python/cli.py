"""Evaluación por línea de comandos: python cli.py <archivo>"""
import sys

from core.document_loader import load_document
from core.rule_engine import evaluar_checklist
from core.scoring import build_summary


def main(path):
    doc = load_document(path)
    resultados = evaluar_checklist(doc["texto"])
    summary = build_summary(resultados)

    print(f"Documento: {path}")
    print(f"Formato: {doc['formato']} | caracteres: {len(doc['texto'])} | páginas: {len(doc['paginas'])}")
    print(f"Puntaje: {summary['puntaje']}% | Cumple: {summary['estados']['cumple']} "
          f"Parcial: {summary['estados']['parcial']} No cumple: {summary['estados']['no_cumple']}")
    print(f"Apto: {'SÍ' if summary['apto'] else 'NO'} "
          f"(críticos fallidos: {', '.join(summary['criticos_fallidos']) or 'ninguno'})")
    print()
    for r in resultados:
        print(f"[{r['estado'].upper():<9}] {r['criterio_id']:>2} | {r['justificacion']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python cli.py <archivo.pdf|docx|imagen>")
        sys.exit(1)
    main(sys.argv[1])
