from pathlib import Path

import pytest

from engine.document_reader import leer_documento, leer_texto
from engine.knowledge_base import cargar_base_conocimiento, criterio_por_id
from engine.recognition import (
    reconocer_criterio,
    reconocer_documento,
    reconocer_subrequisito,
)

PDF_2780477 = Path(
    r"C:\Users\USUARIO\Downloads\CONTRATO 2780477 - INTERDOORS - "
    r"SUMINISTRO PUERTAS DE MADERA ZONAS COMUNES - HEROES.pdf"
)

UNIDADES = [
    {
        "id": "U0001",
        "tipo": "clausula",
        "texto": (
            "El contratante pagara un anticipo equivalente al 40% del valor "
            "total del contrato."
        ),
        "pagina": 1,
        "lineas": [1],
    },
    {
        "id": "U0002",
        "tipo": "clausula",
        "texto": "El saldo del 60% se facturara contra entrega del suministro.",
        "pagina": 1,
        "lineas": [2],
    },
    {
        "id": "U0003",
        "tipo": "campo",
        "texto": "Ret Anticipo: 30 %",
        "pagina": 1,
        "lineas": [3],
    },
]


@pytest.fixture
def criterio_gc02():
    return criterio_por_id(cargar_base_conocimiento(), "GC-02")


def test_anticipo_encuentra_clausula_correcta(criterio_gc02):
    candidatos = reconocer_subrequisito(
        criterio_gc02["subrequisitos"][0], UNIDADES, criterio=criterio_gc02
    )
    assert candidatos[0]["unidad_id"] == "U0001"
    assert candidatos[0]["capa"] == "literal"
    assert candidatos[0]["score"] == 1.0
    assert candidatos[0]["descartable_para_concepto"] is False


def test_retencion_no_se_confunde_con_anticipo(criterio_gc02):
    candidatos = reconocer_subrequisito(
        criterio_gc02["subrequisitos"][0], UNIDADES, criterio=criterio_gc02
    )
    retencion = next(c for c in candidatos if c["unidad_id"] == "U0003")
    assert retencion["contexto"]["es_retencion"] is True
    assert retencion["descartable_para_concepto"] is True
    assert retencion["score"] < 1.0


def test_saldo_encuentra_contra_entrega(criterio_gc02):
    candidatos = reconocer_subrequisito(
        criterio_gc02["subrequisitos"][1], UNIDADES, criterio=criterio_gc02
    )
    assert candidatos[0]["unidad_id"] == "U0002"
    assert "contra entrega" in candidatos[0]["texto"]


def test_credito_sin_evidencia_no_devuelve_candidatos(criterio_gc02):
    candidatos = reconocer_subrequisito(
        criterio_gc02["subrequisitos"][3], UNIDADES, criterio=criterio_gc02
    )
    assert candidatos == []


def test_sin_capa_semantica_sigue_reconociendo(criterio_gc02):
    candidatos = reconocer_subrequisito(
        criterio_gc02["subrequisitos"][0],
        UNIDADES,
        criterio=criterio_gc02,
        usar_semantica=False,
    )
    assert candidatos[0]["unidad_id"] == "U0001"


def test_reconocer_criterio_estructura(criterio_gc02):
    resultado = reconocer_criterio(criterio_gc02, UNIDADES)
    assert resultado["criterio_id"] == "GC-02"
    assert set(resultado["subrequisitos"]) == {
        "GC-02.1", "GC-02.2", "GC-02.3", "GC-02.4",
    }
    assert resultado["mejores"]["GC-02.1"]["unidad_id"] == "U0001"
    assert resultado["mejores"]["GC-02.4"] is None


def test_reconocer_documento_segmenta_y_reconoce():
    base = cargar_base_conocimiento()
    documento = leer_texto(
        "CLÁUSULA PRIMERA. FORMA DE PAGO\n"
        "El contratante pagara un anticipo equivalente al 40% del valor total. "
        "El saldo del 60% se facturara contra entrega del suministro."
    )
    resultado = reconocer_documento(base, documento, criterios=["GC-02"])
    assert set(resultado["criterios"]) == {"GC-02"}
    assert resultado["unidades"]
    gc02 = resultado["criterios"]["GC-02"]
    assert gc02["mejores"]["GC-02.1"] is not None
    assert gc02["mejores"]["GC-02.2"] is not None


@pytest.mark.skipif(not PDF_2780477.exists(), reason="PDF de prueba no disponible")
def test_pdf_real_retencion_y_garantia_no_son_anticipo():
    base = cargar_base_conocimiento()
    documento = leer_documento(PDF_2780477)
    resultado = reconocer_documento(base, documento, criterios=["GC-02"])
    subrequisitos = resultado["criterios"]["GC-02"]["subrequisitos"]

    anticipo = subrequisitos["GC-02.1"]
    assert anticipo
    assert all(c["descartable_para_concepto"] for c in anticipo)
    assert max(c["score"] for c in anticipo) <= 0.3
    assert subrequisitos["GC-02.2"] == []
    assert subrequisitos["GC-02.4"] == []
