from engine import knowledge_base as kb

EXTERNOS_ESPERADOS = {
    "GC-01", "GC-07", "GC-11", "GC-15", "GC-16",
    "GC-17", "GC-18", "GC-19", "GC-20", "GC-21",
    "GC-22", "GC-23", "GC-24", "GC-25",
}


def base():
    return kb.cargar_base_conocimiento()


def test_carga_los_25_criterios_en_orden():
    b = base()
    assert len(b["criterios"]) == 25
    esperados = [f"GC-{numero:02d}" for numero in range(1, 26)]
    assert [c["criterio_id"] for c in b["criterios"]] == esperados


def test_metadatos_de_fuente_y_version():
    b = base()
    assert b["version"] == "1.0"
    assert "V11092025" in b["fuente"]
    assert "Interdoors" in b["fuente"]


def test_gc02_tiene_cuatro_subrequisitos_atomicos():
    criterio = kb.criterio_por_id(base(), "GC-02")
    assert criterio["nombre"] == "Forma de pago"
    assert len(criterio["subrequisitos"]) == 4
    ids = [s["id"] for s in criterio["subrequisitos"]]
    assert ids == ["GC-02.1", "GC-02.2", "GC-02.3", "GC-02.4"]
    assert all(s["texto"] for s in criterio["subrequisitos"])


def test_gc02_conceptos_queries_y_requisito():
    criterio = kb.criterio_por_id(base(), "GC-02")
    assert "40%" in criterio["obligacion"]
    assert any("anticipo" in c.lower() for c in criterio["conceptos"])
    assert len(criterio["queries_semanticas"]) >= 3
    assert all("`" not in q for q in criterio["queries_semanticas"])


def test_subrequisito_condicional_detectado():
    criterio = kb.criterio_por_id(base(), "GC-02")
    assert criterio["subrequisitos"][0]["esencial"] is True
    assert criterio["subrequisitos"][1]["esencial"] is True
    assert criterio["subrequisitos"][2]["condicional"] is True
    assert criterio["subrequisitos"][2]["esencial"] is False


def test_conceptos_relacionados_al_subrequisito():
    criterio = kb.criterio_por_id(base(), "GC-02")
    anticipo = criterio["subrequisitos"][0]
    assert any("anticipo" in c.lower() for c in anticipo["conceptos"])


def test_conceptos_relacionados_evitan_genericos_y_usan_numeros():
    criterio = kb.criterio_por_id(base(), "GC-02")
    anticipo = criterio["subrequisitos"][0]
    assert any("cuarenta por ciento" in c.lower() for c in anticipo["conceptos"])
    assert not any("saldo" in c.lower() for c in anticipo["conceptos"])


def test_seccion_3_marca_evidencia_externa():
    b = base()
    assert set(b["requieren_evidencia_externa"]) == EXTERNOS_ESPERADOS
    assert kb.criterio_por_id(b, "GC-24")["requiere_evidencia_externa"] is True
    assert kb.criterio_por_id(b, "GC-02")["requiere_evidencia_externa"] is False
    assert kb.criterio_por_id(b, "GC-02")["evidencia_externa"] == []


def test_gc01_es_el_unico_con_objetivo_explicito():
    b = base()
    assert kb.criterio_por_id(b, "GC-01")["objetivo"]
    sin_objetivo = [c["criterio_id"] for c in b["criterios"] if not c["objetivo"]]
    assert sin_objetivo == [f"GC-{n:02d}" for n in range(2, 26)]


def test_todos_los_criterios_tienen_contenido():
    for criterio in base()["criterios"]:
        assert criterio["obligacion"], criterio["criterio_id"]
        assert criterio["conceptos"], criterio["criterio_id"]
        assert criterio["subrequisitos"], criterio["criterio_id"]
        assert criterio["reglas_decision"], criterio["criterio_id"]


def test_resumen_coherente():
    r = kb.resumen(base())
    assert r["total_criterios"] == 25
    assert r["total_subrequisitos"] >= 25
    assert r["requieren_evidencia_externa"] == sorted(EXTERNOS_ESPERADOS)
