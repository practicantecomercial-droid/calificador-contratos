from pathlib import Path

import pytest

from engine.document_reader import leer_documento, leer_texto
from engine.knowledge_base import cargar_base_conocimiento
from engine.recognition import reconocer_documento
from engine.schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
)
from engine.validation import validar_documento

PDF_2780477 = Path(
    r"C:\Users\USUARIO\Downloads\CONTRATO 2780477 - INTERDOORS - "
    r"SUMINISTRO PUERTAS DE MADERA ZONAS COMUNES - HEROES.pdf"
)


@pytest.fixture(scope="module")
def base():
    return cargar_base_conocimiento()


def _validar(base, texto):
    documento = leer_texto(texto)
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-14"])
    return validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-14"]
    )["criterios"]["GC-14"]


def _subrequisitos(resultado):
    return {
        subrequisito["subrequisito_id"]: subrequisito
        for subrequisito in resultado["subrequisitos"]
    }


def test_garantia_completa_cumple(base):
    resultado = _validar(
        base,
        "ANEXO DE CONDICIONES DE GARANTÍA - "
        "La garantía de las puertas cubre defectos de fabricación - "
        "Vigencia de 12 meses - "
        "Procedimiento de reclamación ante el área comercial.",
    )
    subs = _subrequisitos(resultado)
    assert resultado["estado"] == ESTADO_CUMPLE
    assert subs["GC-14.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-14.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-14.3"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-14.4"]["estado"] == ESTADO_CUMPLE


def test_garantia_mencionada_sin_detalle_es_parcial(base):
    resultado = _validar(
        base, "La garantía de las puertas está incluida en el suministro."
    )
    assert resultado["estado"] == ESTADO_PARCIAL
    assert resultado["requiere_revision_humana"] is True


def test_anexo_mencionado_pero_incompleto_agrega_faltante(base):
    resultado = _validar(
        base, "Anexo de condiciones de garantía de las puertas."
    )
    assert resultado["estado"] == ESTADO_PARCIAL
    assert (
        "Anexo de condiciones de garantía no adjunto"
        in resultado["informacion_faltante"]
    )
    assert resultado["requiere_revision_humana"] is True


def test_vigencia_sin_duracion_es_parcial(base):
    resultado = _validar(
        base,
        "La garantía de las puertas tiene vigencia según las condiciones del anexo.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-14.3"]["estado"] == ESTADO_PARCIAL


def test_sin_garantia_no_identifica(base):
    resultado = _validar(base, "Suministro de puertas de madera.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


@pytest.mark.skipif(not PDF_2780477.exists(), reason="PDF de prueba no disponible")
def test_pdf_real_garantia_incompleta(base):
    documento = leer_documento(PDF_2780477)
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-14"])
    resultado = validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-14"]
    )["criterios"]["GC-14"]

    assert resultado["estado"] == ESTADO_PARCIAL
    assert resultado["requiere_revision_humana"] is True
