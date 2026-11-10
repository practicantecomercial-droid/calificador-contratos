from pathlib import Path

import pytest

from engine.document_reader import leer_documento, leer_texto
from engine.knowledge_base import cargar_base_conocimiento, criterio_por_id
from engine.recognition import reconocer_documento
from engine.schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
)
from engine.validation import validar_criterio, validar_documento
from engine.validation.gc02 import validar_gc02

PDF_2780477 = Path(
    r"C:\Users\USUARIO\Downloads\CONTRATO 2780477 - INTERDOORS - "
    r"SUMINISTRO PUERTAS DE MADERA ZONAS COMUNES - HEROES.pdf"
)


@pytest.fixture(scope="module")
def base():
    return cargar_base_conocimiento()


@pytest.fixture(scope="module")
def criterio_gc02(base):
    return criterio_por_id(base, "GC-02")


def _validar(base, texto):
    documento = leer_texto(texto)
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-02"])
    return validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-02"]
    )["criterios"]["GC-02"]


def _subrequisitos(resultado):
    return {
        subrequisito["subrequisito_id"]: subrequisito
        for subrequisito in resultado["subrequisitos"]
    }


def test_forma_de_pago_completa_cumple(base):
    resultado = _validar(
        base,
        "CLÁUSULA PRIMERA. FORMA DE PAGO\n"
        "El contratante pagará un anticipo equivalente al 40% del valor total "
        "del contrato. El saldo del 60% se facturará contra entrega del suministro.",
    )
    subs = _subrequisitos(resultado)
    assert resultado["estado"] == ESTADO_CUMPLE
    assert resultado["requiere_revision_humana"] is False
    assert subs["GC-02.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-02.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-02.3"]["estado"] == ESTADO_NO_APLICA
    assert subs["GC-02.4"]["estado"] == ESTADO_NO_APLICA


def test_anticipo_distinto_de_40_no_cumple(base):
    resultado = _validar(
        base,
        "CLÁUSULA PRIMERA. FORMA DE PAGO\n"
        "El contratante pagará un anticipo equivalente al 30% del valor total "
        "del contrato. El saldo del 60% se pagará contra entrega del suministro.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-02.1"]["estado"] == ESTADO_NO_CUMPLE
    assert resultado["estado"] == ESTADO_NO_CUMPLE


def test_facturaciones_parciales_sin_amortizacion_es_parcial(base):
    resultado = _validar(
        base,
        "CLÁUSULA PRIMERA. FORMA DE PAGO\n"
        "El contratante pagará un anticipo equivalente al 40% del valor total "
        "del contrato. El saldo del 60% se pagará contra entrega del suministro. "
        "Se realizarán facturaciones parciales según actas parciales.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-02.3"]["estado"] == ESTADO_PARCIAL
    assert resultado["estado"] == ESTADO_PARCIAL
    assert resultado["requiere_revision_humana"] is True


def test_credito_sin_autorizacion_exige_revision(base):
    resultado = _validar(
        base,
        "CLÁUSULA PRIMERA. FORMA DE PAGO\n"
        "El contratante pagará un anticipo equivalente al 40% del valor total "
        "del contrato. El saldo del 60% se pagará contra entrega del suministro. "
        "El saldo se pagará a crédito a 30 días.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-02.4"]["estado"] == ESTADO_REVISION_HUMANA
    assert resultado["estado"] == ESTADO_REVISION_HUMANA


def test_credito_autorizado_cumple(base):
    resultado = _validar(
        base,
        "CLÁUSULA PRIMERA. FORMA DE PAGO\n"
        "El contratante pagará un anticipo equivalente al 40% del valor total "
        "del contrato. El saldo del 60% se pagará contra entrega del suministro. "
        "El saldo se pagará a crédito a 30 días con aprobación de crédito del área.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-02.4"]["estado"] == ESTADO_CUMPLE
    assert resultado["estado"] == ESTADO_CUMPLE


def test_registro_usa_regla_especifica(base, criterio_gc02):
    reconocimiento = {
        "criterio_id": "GC-02",
        "subrequisitos": {
            "GC-02.1": [],
            "GC-02.2": [],
            "GC-02.3": [],
            "GC-02.4": [],
        },
    }
    resultado = validar_criterio(criterio_gc02, reconocimiento)
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultado["subrequisitos"]


def test_gc02_directo_sin_evidencia_no_identifica(criterio_gc02):
    reconocimiento = {
        "criterio_id": "GC-02",
        "subrequisitos": {
            "GC-02.1": [],
            "GC-02.2": [],
            "GC-02.3": [],
            "GC-02.4": [],
        },
    }
    resultado = validar_gc02(criterio_gc02, reconocimiento, texto_documento="")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultado["confianza"] == 0.0


@pytest.mark.skipif(not PDF_2780477.exists(), reason="PDF de prueba no disponible")
def test_pdf_real_sin_forma_de_pago_queda_no_identificado(base):
    documento = leer_documento(PDF_2780477)
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-02"])
    resultado = validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-02"]
    )["criterios"]["GC-02"]
    subs = _subrequisitos(resultado)

    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert subs["GC-02.1"]["estado"] == ESTADO_NO_IDENTIFICADO
    assert subs["GC-02.2"]["estado"] == ESTADO_NO_IDENTIFICADO
    assert subs["GC-02.3"]["estado"] == ESTADO_NO_APLICA
    assert subs["GC-02.4"]["estado"] == ESTADO_NO_APLICA
    assert "Forma de pago vacía en el contrato" in resultado["informacion_faltante"]
    assert resultado["requiere_revision_humana"] is True
