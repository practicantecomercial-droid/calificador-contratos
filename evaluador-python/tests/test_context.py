from pathlib import Path

import pytest

from engine.context import (
    construir_contexto,
    parsear_fecha,
    parsear_numero,
    parsear_porcentaje,
)
from engine.document_reader import leer_documento

PDF_2780477 = Path(
    r"C:\Users\USUARIO\Downloads\CONTRATO 2780477 - INTERDOORS - "
    r"SUMINISTRO PUERTAS DE MADERA ZONAS COMUNES - HEROES.pdf"
)


def test_contexto_erp(documento_erp):
    contexto = construir_contexto(documento_erp)
    assert contexto["numero_contrato"] == "2780477"
    assert contexto["tipo_contrato"] == "SUMINISTRO DE MATERIALES OBRA"
    assert contexto["valor"] == 17746429.54
    assert contexto["moneda"] == "COP"
    assert contexto["estado"] == "Por Aprobación"
    assert contexto["fecha_inicio"] == "2026-03-04"
    assert contexto["fecha_fin"] == "2026-04-30"
    assert contexto["plazo_dias"] == 57


def test_contexto_porcentajes_y_forma_pago(documento_erp):
    contexto = construir_contexto(documento_erp)
    assert contexto["porcentajes"]["ret_anticipo"] == 30.0
    assert contexto["porcentajes"]["ret_garantias"] == 10.0
    assert contexto["porcentajes"]["iva"] == 19.0
    assert contexto["forma_pago"]["vacia"] is True
    assert "forma de pago" in contexto["campos_vacios"]


def test_contexto_partes_y_clasificacion(documento_erp):
    contexto = construir_contexto(documento_erp)
    assert contexto["contratante"]["empresa"] == "CONSTRUCCIONES BUEN VIVIR S.A.S."
    assert contexto["contratista"]["nombre"] == "INTERDOORS SAS"
    assert contexto["contratista"]["ciudad"] == "GIRARDOTA"
    assert contexto["es_suministro"] is True
    assert contexto["es_instalacion"] is False
    assert contexto["es_constructora"] is True


def test_contexto_polizas_mencionadas(documento_erp):
    contexto = construir_contexto(documento_erp)
    assert set(contexto["polizas_mencionadas"]) == {
        "buen_manejo_anticipo", "cumplimiento", "calidad",
    }


def test_parsear_numero_formatos():
    assert parsear_numero("17,746,429.54") == 17746429.54
    assert parsear_numero("4.473.889") == 4473889.0
    assert parsear_numero("0.00") == 0.0
    assert parsear_numero("") is None
    assert parsear_numero("sin cifras") is None


def test_parsear_porcentaje_formatos():
    assert parsear_porcentaje("30 %") == 30.0
    assert parsear_porcentaje("19 % 2,833,463.54") == 19.0
    assert parsear_porcentaje("0.00 %") == 0.0
    assert parsear_porcentaje("sin dato") is None


def test_parsear_fecha_formatos():
    assert parsear_fecha("04/03/2026") == "2026-03-04"
    assert parsear_fecha("30/04/2026") == "2026-04-30"
    assert parsear_fecha("") is None
    assert parsear_fecha("31/02/2026") is None


@pytest.mark.skipif(not PDF_2780477.exists(), reason="PDF de prueba no disponible")
def test_contexto_pdf_real_2780477():
    contexto = construir_contexto(leer_documento(PDF_2780477))
    assert contexto["tipo_contrato"] == "SUMINISTRO DE MATERIALES OBRA"
    assert contexto["valor"] == 17746429.54
    assert contexto["estado"] == "Por Aprobación"
    assert contexto["porcentajes"]["ret_anticipo"] == 30.0
    assert contexto["forma_pago"]["vacia"] is True
    assert contexto["es_suministro"] is True
    assert contexto["es_instalacion"] is False
