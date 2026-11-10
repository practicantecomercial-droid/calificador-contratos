import pytest

from engine import gc_mapping
from engine import knowledge_base as kb


def test_mapa_gc_numero_completo():
    assert len(gc_mapping.GC_A_NUMERO) == 25
    assert len(gc_mapping.NUMERO_A_GC) == 25
    assert gc_mapping.gc_a_numero("GC-01") == 1
    assert gc_mapping.gc_a_numero("GC-25") == 25
    assert gc_mapping.numero_a_gc(14) == "GC-14"


def test_mapeo_invalido_falla():
    with pytest.raises(ValueError):
        gc_mapping.gc_a_numero("GC-99")
    with pytest.raises(ValueError):
        gc_mapping.numero_a_gc(0)


def test_fusion_metadatos_legacy():
    base = kb.cargar_base_conocimiento()
    gc_mapping.fusionar_metadatos(base)
    criterio = kb.criterio_por_id(base, "GC-02")
    assert criterio["categoria"] == "economica"
    assert criterio["peso"] == 10
    assert criterio["critico"] is True
    assert criterio["minimo_subitems"] == 2
    assert criterio["nombre_legacy"] == "Forma de pago"


def test_fusion_metadatos_todos_mapean():
    base = kb.cargar_base_conocimiento()
    gc_mapping.fusionar_metadatos(base)
    for criterio in base["criterios"]:
        assert criterio["categoria"], criterio["criterio_id"]
        assert criterio["peso"] >= 1
