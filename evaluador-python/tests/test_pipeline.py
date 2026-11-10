import json
from pathlib import Path

import pytest

from engine.document_reader import leer_texto
from engine.knowledge_base import cargar_base_conocimiento
from engine.pipeline import evaluar_archivo, evaluar_documento
from engine.schema import ESTADO_CUMPLE, ESTADO_NO_IDENTIFICADO

PDF_2780477 = Path(
    r"C:\Users\USUARIO\Downloads\CONTRATO 2780477 - INTERDOORS - "
    r"SUMINISTRO PUERTAS DE MADERA ZONAS COMUNES - HEROES.pdf"
)

TEXTO_COMPLETO = (
    "CLÁUSULA PRIMERA. FORMA DE PAGO\n"
    "El contratante pagará un anticipo equivalente al 40% del valor total "
    "del contrato. El saldo del 60% se facturará contra entrega del suministro."
)


def test_reporte_completo_de_25_criterios():
    reporte = evaluar_documento(leer_texto(TEXTO_COMPLETO))
    esperados = {f"GC-{numero:02d}" for numero in range(1, 26)}

    assert set(reporte["resultados"]) == esperados
    assert len(reporte["criterios"]) == 25
    assert reporte["resumen"]["total_criterios"] == 25
    assert sum(reporte["resumen"]["conteo_estados"].values()) == 25
    assert reporte["unidades"] > 0


def test_gc02_usa_regla_especifica_y_metadatos():
    reporte = evaluar_documento(leer_texto(TEXTO_COMPLETO))
    gc02 = reporte["resultados"]["GC-02"]

    assert gc02["estado"] == ESTADO_CUMPLE
    assert gc02["peso"] == 10
    assert gc02["critico"] is True
    assert gc02["categoria"] == "economica"


def test_metadatos_se_pueden_desactivar():
    reporte = evaluar_documento(
        leer_texto(TEXTO_COMPLETO), metadatos=False
    )
    gc02 = reporte["resultados"]["GC-02"]

    assert gc02["peso"] == 1
    assert gc02["critico"] is False
    assert gc02["categoria"] == ""


def test_criterios_limitados():
    reporte = evaluar_documento(
        leer_texto(TEXTO_COMPLETO), criterios=["GC-02"]
    )
    assert set(reporte["resultados"]) == {"GC-02"}
    assert reporte["resumen"]["total_criterios"] == 1


def test_reporte_es_json_serializable():
    reporte = evaluar_documento(leer_texto(TEXTO_COMPLETO))
    serializado = json.dumps(reporte, ensure_ascii=False)
    assert '"GC-02"' in serializado


def test_advertencias_detectan_forma_de_pago_vacia(documento_erp):
    reporte = evaluar_documento(documento_erp, criterios=["GC-02"])
    assert any(
        "Forma de pago vacía" in advertencia
        for advertencia in reporte["advertencias"]
    )


@pytest.mark.skipif(not PDF_2780477.exists(), reason="PDF de prueba no disponible")
def test_pdf_real_genera_reporte_auditable():
    base = cargar_base_conocimiento()
    reporte = evaluar_archivo(PDF_2780477)

    assert len(reporte["criterios"]) == 25
    assert reporte["resultados"]["GC-02"]["estado"] == ESTADO_NO_IDENTIFICADO
    assert reporte["resumen"]["apto"] is False
    assert "GC-02" in reporte["resumen"]["criticos_sin_evidencia"]
    assert set(reporte["resumen"]["evidencia_externa_pendiente"]) == set(
        base["requieren_evidencia_externa"]
    )
    assert reporte["documento"]["paginas"] == 1
    assert reporte["documento"]["caracteres"] > 1000
