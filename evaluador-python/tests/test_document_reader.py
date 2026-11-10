from pathlib import Path

import pytest

from engine.document_reader import leer_documento

PDF_2780477 = Path(
    r"C:\Users\USUARIO\Downloads\CONTRATO 2780477 - INTERDOORS - "
    r"SUMINISTRO PUERTAS DE MADERA ZONAS COMUNES - HEROES.pdf"
)


def test_lee_campos_erp(documento_erp):
    campos = documento_erp["campos"]
    assert campos["tipo contrato"]["valor"] == "SUMINISTRO DE MATERIALES OBRA"
    assert campos["valor contrato"]["valor"] == "17,746,429.54"
    assert campos["estado"]["valor"] == "Por Aprobación"
    assert campos["ret anticipo"]["valor"] == "30 %"
    assert campos["ret garantias"]["valor"] == "10 %"
    assert campos["iva"]["valor"].startswith("19 %")
    assert campos["descripcion"]["valor"].startswith("SUMINISTRO DE PUERTAS")


def test_detecta_campos_vacios(documento_erp):
    assert "forma de pago" in documento_erp["campos_vacios"]
    assert "referencia" in documento_erp["campos_vacios"]
    assert documento_erp["campos"]["forma de pago"]["vacio"] is True


def test_observaciones_no_se_corta_por_dos_puntos_internos(documento_erp):
    observaciones = documento_erp["campos"]["observaciones"]["valor"]
    assert "BUEN MANEJO DE ANTICIPO" in observaciones
    assert "POLIZA DE CUMPLIMIENTO" in observaciones
    assert "CALIDAD DEL MATERIALES" in observaciones
    assert "CANTIDADES DE OBRA" not in observaciones


def test_detecta_bloque_cabecera(documento_erp):
    bloque = documento_erp["bloques"][0]
    assert bloque["campos"]["empresa"] == "CONSTRUCCIONES BUEN VIVIR S.A.S."
    assert bloque["campos"]["nit"] == "900085546"


def test_ciudad_no_arrastra_titulo_de_seccion(documento_erp):
    assert documento_erp["campos"]["ciudad"]["valor"] == "GIRARDOTA"


def test_lineas_y_paginas(documento_erp):
    assert documento_erp["formato"] == "texto"
    assert documento_erp["paginas"][0]["pagina"] == 1
    assert documento_erp["lineas"][0]["n"] == 1
    assert all("pagina" in linea for linea in documento_erp["lineas"])


@pytest.mark.skipif(not PDF_2780477.exists(), reason="PDF de prueba no disponible")
def test_pdf_real_2780477():
    documento = leer_documento(PDF_2780477)
    assert documento["formato"] == "pdf"
    assert documento["paginas"][0]["ocr"] is False
    assert documento["campos"]["tipo contrato"]["valor"] == "SUMINISTRO DE MATERIALES OBRA"
    assert documento["campos"]["forma de pago"]["vacio"] is True
    assert documento["campos"]["ret anticipo"]["valor"] == "30 %"
    assert documento["campos"]["ret garantias"]["valor"] == "10 %"
