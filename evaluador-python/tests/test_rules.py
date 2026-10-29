from core import rule_engine


def test_polizas_parcial_con_dos_polizas():
    criterio = {
        "id": 9, "nombre": "Pólizas", "minimo_subitems": 4,
        "subitems": [
            {"nombre": "Cumplimiento", "terminos": ["poliza de cumplimiento", "cumplimiento"]},
            {"nombre": "Buen manejo", "terminos": ["buen manejo"]},
            {"nombre": "Salarios (3 años)", "terminos": ["salarios"], "patron": {"tipo": "plazo", "unidad": "años", "valor": 3, "comparacion": ">="}},
            {"nombre": "Calidad (12 meses)", "terminos": ["calidad"], "patron": {"tipo": "plazo", "unidad": "meses", "valor": 12, "comparacion": ">="}},
            {"nombre": "Responsabilidad civil", "terminos": ["responsabilidad civil"]},
            {"nombre": "Tope 100%", "patron": {"tipo": "porcentaje", "valor": 100}},
        ],
    }
    texto = "POLIZA DE BUEN MANEJO DE ANTICIPO 30%. POLIZA DE CUMPLIMIENTO 20%. Ret Anticipo 30%."
    r = rule_engine.evaluar_criterio(criterio, rule_engine.tc.normalize_text(texto), texto)
    assert r["estado"] == "parcial"
    assert "Responsabilidad civil" in r["faltantes"]


def test_forma_pago_no_cumple_solo_anticipo_30():
    criterio = {
        "id": 2, "nombre": "Forma de pago", "minimo_subitems": 2,
        "subitems": [
            {"nombre": "Anticipo 40%", "terminos": ["anticipo"], "patron": {"tipo": "porcentaje", "valor": 40}},
            {"nombre": "Saldo 60%", "terminos": ["saldo"], "patron": {"tipo": "porcentaje", "valor": 60}},
        ],
    }
    texto = "Ret Anticipo 30% y Ret Garantias 10%"
    r = rule_engine.evaluar_criterio(criterio, rule_engine.tc.normalize_text(texto), texto)
    assert r["estado"] == "no_cumple"


def test_forma_pago_cumple_con_40_y_60():
    criterio = {
        "id": 2, "nombre": "Forma de pago", "minimo_subitems": 2,
        "subitems": [
            {"nombre": "Anticipo 40%", "terminos": ["anticipo"], "patron": {"tipo": "porcentaje", "valor": 40}},
            {"nombre": "Saldo 60%", "terminos": ["saldo"], "patron": {"tipo": "porcentaje", "valor": 60}},
        ],
    }
    texto = "Anticipo del 40% y saldo del 60% contra entrega."
    r = rule_engine.evaluar_criterio(criterio, rule_engine.tc.normalize_text(texto), texto)
    assert r["estado"] == "cumple"


def test_negacion_unilateral_invalida_bilateralidad():
    criterio = {
        "id": 8, "nombre": "Multas", "minimo_subitems": 2,
        "subitems": [
            {"nombre": "Multa", "terminos": ["multa", "clausula penal"]},
            {"nombre": "Bilateral", "terminos": ["bilateral", "mutuo acuerdo"], "negacion": ["unilateral"]},
        ],
    }
    texto = "No se aceptarán multas unilaterales."
    r = rule_engine.evaluar_criterio(criterio, rule_engine.tc.normalize_text(texto), texto)
    assert r["estado"] == "parcial"  # "multa" sí, "bilateral" no


def test_evaluar_checklist_carga_yaml():
    resultados = rule_engine.evaluar_checklist("documento vacío de prueba")
    assert len(resultados) == 25
