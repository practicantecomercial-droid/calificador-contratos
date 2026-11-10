from pathlib import Path

import pytest

from engine.document_reader import leer_documento, leer_texto
from engine.knowledge_base import cargar_base_conocimiento
from engine.recognition import reconocer_documento
from engine.schema import (
    ALCANCE_EVIDENCIA_EXTERNA,
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
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-16"])
    return validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-16"]
    )["criterios"]["GC-16"]


def _subrequisitos(resultado):
    return {
        subrequisito["subrequisito_id"]: subrequisito
        for subrequisito in resultado["subrequisitos"]
    }


def test_requisitos_completos_cumplen(base):
    resultado = _validar(
        base,
        "Se anexan dos copias de los documentos del contrato - "
        "Firma previa del director comercial - "
        "Cotizaciones firmadas y actualizadas.",
    )
    subs = _subrequisitos(resultado)
    assert resultado["estado"] == ESTADO_CUMPLE
    assert subs["GC-16.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-16.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-16.3"]["estado"] == ESTADO_CUMPLE


def test_copias_sin_evidencia_es_parcial_y_externa(base):
    resultado = _validar(
        base, "Se requieren dos copias de los documentos del contrato."
    )
    assert resultado["estado"] == ESTADO_PARCIAL
    assert resultado["alcance"] == ALCANCE_EVIDENCIA_EXTERNA
    assert "Copias contractuales y cotizaciones firmadas" in resultado[
        "informacion_faltante"
    ]
    assert resultado["requiere_revision_humana"] is True


def test_firma_de_gerencia_sin_director_comercial_es_parcial(base):
    resultado = _validar(
        base, "El contrato se remite para firma de gerencia."
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-16.2"]["estado"] == ESTADO_PARCIAL


def test_sin_requisitos_no_identifica_y_marca_externa(base):
    resultado = _validar(base, "Suministro de puertas de madera.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultado["alcance"] == ALCANCE_EVIDENCIA_EXTERNA
    assert resultado["requiere_revision_humana"] is True


@pytest.mark.skipif(not PDF_2780477.exists(), reason="PDF de prueba no disponible")
def test_pdf_real_sin_requisitos_de_firma(base):
    documento = leer_documento(PDF_2780477)
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-16"])
    resultado = validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-16"]
    )["criterios"]["GC-16"]

    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultado["alcance"] == ALCANCE_EVIDENCIA_EXTERNA
    assert "Copias contractuales y cotizaciones firmadas" in resultado[
        "informacion_faltante"
    ]
    assert resultado["requiere_revision_humana"] is True
