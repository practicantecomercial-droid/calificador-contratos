from pathlib import Path

import pytest

from engine.document_reader import leer_documento, leer_texto
from engine.knowledge_base import cargar_base_conocimiento
from engine.recognition import reconocer_documento
from engine.schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
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
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-09"])
    return validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-09"]
    )["criterios"]["GC-09"]


def _subrequisitos(resultado):
    return {
        subrequisito["subrequisito_id"]: subrequisito
        for subrequisito in resultado["subrequisitos"]
    }


def test_polizas_completas_cumplen(base):
    resultado = _validar(
        base,
        "GARANTÍAS Y SEGUROS - PÓLIZA DE CUMPLIMIENTO 10% - "
        "PÓLIZA DE BUEN MANEJO DEL ANTICIPO 30% - "
        "PÓLIZA DE SALARIOS CON VIGENCIA DE 36 MESES - "
        "PÓLIZA DE CALIDAD CON VIGENCIA DE 12 MESES",
    )
    subs = _subrequisitos(resultado)
    assert resultado["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.3"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.4"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.5"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.6"]["estado"] == ESTADO_NO_APLICA


def test_salarios_con_vigencia_insuficiente_no_cumple(base):
    resultado = _validar(
        base,
        "PÓLIZA DE CUMPLIMIENTO 10% - PÓLIZA DE BUEN MANEJO DEL ANTICIPO 30% - "
        "PÓLIZA DE SALARIOS CON VIGENCIA DE 12 MESES - "
        "PÓLIZA DE CALIDAD CON VIGENCIA DE 12 MESES",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-09.3"]["estado"] == ESTADO_NO_CUMPLE
    assert resultado["estado"] == ESTADO_NO_CUMPLE


def test_salarios_con_excepcion_aprobada_requiere_revision(base):
    resultado = _validar(
        base,
        "PÓLIZA DE CUMPLIMIENTO 10% - PÓLIZA DE BUEN MANEJO DEL ANTICIPO 30% - "
        "PÓLIZA DE SALARIOS CON VIGENCIA DE 12 MESES - "
        "PÓLIZA DE CALIDAD CON VIGENCIA DE 12 MESES - "
        "EXCEPCIÓN APROBADA POR EL JEFE ADMINISTRATIVO",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-09.3"]["estado"] == ESTADO_REVISION_HUMANA
    assert subs["GC-09.6"]["estado"] == ESTADO_CUMPLE


def test_sin_polizas_no_identifica(base):
    resultado = _validar(base, "Las partes acuerdan el suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultado["confianza"] == 0.0


def test_suma_de_polizas_superior_al_100_no_cumple(base):
    resultado = _validar(
        base,
        "PÓLIZA DE CUMPLIMIENTO 60% - PÓLIZA DE BUEN MANEJO DEL ANTICIPO 50%",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-09.5"]["estado"] == ESTADO_NO_CUMPLE
    assert resultado["estado"] == ESTADO_NO_CUMPLE


@pytest.mark.skipif(not PDF_2780477.exists(), reason="PDF de prueba no disponible")
def test_pdf_real_polizas_cumplen(base):
    documento = leer_documento(PDF_2780477)
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-09"])
    resultado = validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-09"]
    )["criterios"]["GC-09"]
    subs = _subrequisitos(resultado)

    assert resultado["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.3"]["estado"] == ESTADO_NO_APLICA
    assert subs["GC-09.4"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.5"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-09.6"]["estado"] == ESTADO_NO_APLICA
