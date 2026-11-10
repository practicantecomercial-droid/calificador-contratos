"""Evaluación por línea de comandos: python cli.py <archivo> [opciones]."""
from __future__ import annotations

import argparse
import json
import sys

from engine import evaluar_archivo, evaluar_archivo_con_expediente


def _lista(valor):
    if not valor:
        return None
    return [item.strip().upper() for item in valor.split(",") if item.strip()]


def _rutas(valor):
    if not valor:
        return None
    return [item.strip() for item in valor.split(",") if item.strip()]


def _imprimir_resumen(reporte):
    documento = reporte["documento"]
    resumen = reporte["resumen"]

    print(f"Documento: {documento['ruta']}")
    print(
        f"Formato: {documento['formato']} | páginas: {documento['paginas']} "
        f"| caracteres: {documento['caracteres']}"
    )
    print(
        f"Puntaje: {resumen['puntaje']}% | "
        f"confianza promedio: {resumen['confianza_promedio']}"
    )
    print(
        "Estados: "
        + " | ".join(
            f"{estado}: {total}"
            for estado, total in resumen["conteo_estados"].items()
        )
    )
    print(f"Apto: {'SÍ' if resumen['apto'] else 'NO'}")

    for etiqueta, clave in (
        ("Críticos no cumplidos", "criticos_no_cumplidos"),
        ("Críticos sin evidencia", "criticos_sin_evidencia"),
        ("Críticos en revisión", "criticos_en_revision"),
    ):
        if resumen[clave]:
            print(f"{etiqueta}: {', '.join(resumen[clave])}")

    if resumen["evidencia_externa_pendiente"]:
        print(
            "Evidencia externa pendiente: "
            + ", ".join(resumen["evidencia_externa_pendiente"])
        )

    expediente = reporte.get("expediente")
    if expediente:
        print(
            f"Expediente: {len(expediente['archivos'])} archivo(s) | "
            f"{len(expediente['errores'])} error(es)"
        )
        for error in expediente["errores"]:
            print(f"ERROR EXPEDIENTE: {error['archivo']}: {error['error']}")

    for advertencia in reporte["advertencias"]:
        print(f"ADVERTENCIA: {advertencia}")


def _imprimir_criterios(reporte):
    print()
    for resultado in reporte["criterios"]:
        marca = " [CRÍTICO]" if resultado.get("critico") else ""
        print(
            f"[{resultado['estado']:<16}] {resultado['criterio_id']} "
            f"{resultado['criterio']}{marca}"
        )
        print(
            f"    confianza: {resultado['confianza']:.2f} | "
            f"alcance: {resultado['alcance']}"
        )
        if resultado["observacion"]:
            print(f"    {resultado['observacion']}")
        documental = resultado.get("resultado_documental")
        if documental:
            print(f"    documental: {documental['estado']}")
        externo = resultado.get("resultado_expediente")
        if externo:
            print(
                f"    expediente: {externo['estado']} | "
                f"{externo['observacion']}"
            )
        if resultado["informacion_faltante"]:
            print("    Faltante: " + "; ".join(resultado["informacion_faltante"]))
        for contradiccion in resultado["contradicciones"]:
            print(
                f"    Contradicción en {contradiccion['subrequisito_id']}: "
                f"{contradiccion['texto']}"
            )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Evalúa un contrato contra los 25 criterios de Interdoors."
    )
    parser.add_argument("archivo", help="Ruta del contrato (PDF, DOCX o imagen).")
    parser.add_argument(
        "--criterios",
        help="Lista separada por comas de criterios GC-XX a evaluar.",
    )
    parser.add_argument(
        "--expediente",
        help="Carpeta o archivos separados por comas con la evidencia externa.",
    )
    parser.add_argument(
        "--sin-semantica",
        action="store_true",
        help="Desactiva la capa semántica y usa solo coincidencias léxicas.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime el reporte completo en JSON.",
    )
    args = parser.parse_args(argv)

    try:
        if args.expediente:
            reporte = evaluar_archivo_con_expediente(
                args.archivo,
                _rutas(args.expediente),
                criterios=_lista(args.criterios),
                usar_semantica=not args.sin_semantica,
            )
        else:
            reporte = evaluar_archivo(
                args.archivo,
                criterios=_lista(args.criterios),
                usar_semantica=not args.sin_semantica,
            )
    except FileNotFoundError:
        print(f"No existe el archivo: {args.archivo}", file=sys.stderr)
        return 2
    except (ValueError, RuntimeError) as error:
        print(f"No se pudo leer el documento: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(reporte, ensure_ascii=False, indent=2, default=str))
    else:
        _imprimir_resumen(reporte)
        _imprimir_criterios(reporte)
    return 0


if __name__ == "__main__":
    sys.exit(main())
