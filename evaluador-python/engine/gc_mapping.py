"""Compatibilidad entre los identificadores GC-XX y la lista 1..25."""
from __future__ import annotations

from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CHECKLIST_PATH = BASE_DIR / "rules" / "checklist.yaml"

GC_A_NUMERO = {f"GC-{numero:02d}": numero for numero in range(1, 26)}
NUMERO_A_GC = {numero: gc for gc, numero in GC_A_NUMERO.items()}


def gc_a_numero(criterio_id):
    try:
        return GC_A_NUMERO[criterio_id]
    except KeyError as exc:
        raise ValueError(f"Identificador GC no válido: {criterio_id!r}") from exc


def numero_a_gc(numero):
    try:
        return NUMERO_A_GC[int(numero)]
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError(f"Número de criterio no válido: {numero!r}") from exc


def cargar_checklist_legacy(ruta=None):
    path = Path(ruta) if ruta else DEFAULT_CHECKLIST_PATH
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("criterios", [])


def fusionar_metadatos(base, checklist=None):
    """Añade categoria/peso/critico del checklist histórico (1..25) al motor."""
    checklist = checklist if checklist is not None else cargar_checklist_legacy()
    legacy = {criterio["id"]: criterio for criterio in checklist}

    for criterio in base["criterios"]:
        antiguo = legacy.get(criterio["numero"])
        if not antiguo:
            continue
        criterio["categoria"] = antiguo.get("categoria", criterio.get("categoria", ""))
        criterio["peso"] = antiguo.get("peso", criterio.get("peso", 1))
        criterio["critico"] = antiguo.get("critico", criterio.get("critico", False))
        criterio["minimo_subitems"] = antiguo.get(
            "minimo_subitems", len(criterio["subrequisitos"])
        )
        criterio["nombre_legacy"] = antiguo.get("nombre", "")
    return base
