import pytest

from engine.document_reader import leer_texto
from engine.knowledge_base import cargar_base_conocimiento
from engine.recognition import reconocer_documento
from engine.schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
)
from engine.validation import validar_documento


@pytest.fixture(scope="module")
def base():
    return cargar_base_conocimiento()


def _validar(base, criterio, texto):
    documento = leer_texto(texto)
    reconocimiento = reconocer_documento(base, documento, criterios=[criterio])
    return validar_documento(
        base, reconocimiento, documento=documento, criterios=[criterio]
    )["criterios"][criterio]


def _subrequisitos(resultado):
    return {
        subrequisito["subrequisito_id"]: subrequisito
        for subrequisito in resultado["subrequisitos"]
    }


def test_gc07_referencia_completa(base):
    resultado = _validar(
        base,
        "GC-07",
        "El contrato hace referencia a la cotizacion numero COT-2026-001 con "
        "fecha de elaboracion 15/02/2026; la poliza coincide con la cotizacion.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-07.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-07.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-07.3"]["estado"] == ESTADO_CUMPLE


def test_gc07_sin_numero_es_parcial(base):
    resultado = _validar(base, "GC-07", "Se menciona la cotizacion.")
    assert resultado["estado"] == ESTADO_PARCIAL
    subs = _subrequisitos(resultado)
    assert subs["GC-07.1"]["estado"] == ESTADO_PARCIAL


def test_gc07_poliza_sin_coincidencia_es_parcial(base):
    resultado = _validar(
        base,
        "GC-07",
        "La poliza se expide con ocasion de la cotizacion.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-07.3"]["estado"] == ESTADO_PARCIAL


def test_gc08_sin_multas_no_aplica(base):
    resultado = _validar(base, "GC-08", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_APLICA


def test_gc08_multa_bilateral_cumple(base):
    resultado = _validar(
        base,
        "GC-08",
        "Se pacta clausula penal bilateral aplicable a ambas partes, con "
        "obligaciones reciprocas.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-08.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-08.3"]["estado"] == ESTADO_CUMPLE


def test_gc08_multa_unilateral_no_cumple(base):
    resultado = _validar(
        base,
        "GC-08",
        "Se pacta multa unilateral a cargo del contratista.",
    )
    assert resultado["estado"] == ESTADO_NO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-08.2"]["estado"] == ESTADO_NO_CUMPLE


def test_gc10_ajuste_completo(base):
    resultado = _validar(
        base,
        "GC-10",
        "Se contempla ajuste de valores por demora en la ejecucion por causas "
        "ajenas a Interdoors, conforme a variaciones del mercado, mediante anexo "
        "complementario con el jefe administrativo.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-10.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-10.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-10.3"]["estado"] == ESTADO_CUMPLE


def test_gc10_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-10", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    subs = _subrequisitos(resultado)
    assert subs["GC-10.1"]["estado"] == ESTADO_NO_APLICA


def test_gc10_solo_demora_es_parcial(base):
    resultado = _validar(
        base, "GC-10", "El contrato regula la demora en la entrega."
    )
    assert resultado["estado"] == ESTADO_PARCIAL


def test_gc11_liquidacion_completa(base):
    resultado = _validar(
        base,
        "GC-11",
        "Los documentos para la liquidacion de la obra son acta de liquidacion y "
        "paz y salvo; se anexan y se remiten, con firma del director comercial.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-11.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-11.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-11.3"]["estado"] == ESTADO_NO_APLICA
    assert subs["GC-11.4"]["estado"] == ESTADO_CUMPLE


def test_gc11_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-11", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc11_lista_sin_entrega_es_parcial(base):
    resultado = _validar(
        base,
        "GC-11",
        "Los documentos para la liquidacion de la obra son acta y paz y salvo.",
    )
    assert resultado["estado"] == ESTADO_PARCIAL
    subs = _subrequisitos(resultado)
    assert subs["GC-11.2"]["estado"] == ESTADO_PARCIAL


def test_gc12_devolucion_completa(base):
    resultado = _validar(
        base,
        "GC-12",
        "La devolucion del retenido se realizara dentro de 30 dias siguientes a "
        "la liquidacion, previo paz y salvo y cumplimiento de las condiciones de "
        "liberacion.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-12.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-12.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-12.3"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-12.4"]["estado"] == ESTADO_CUMPLE


def test_gc12_sin_retencion_no_identifica(base):
    resultado = _validar(base, "GC-12", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc12_solo_retencion_es_parcial(base):
    resultado = _validar(
        base, "GC-12", "Se aplica una retencion del 10%."
    )
    assert resultado["estado"] == ESTADO_PARCIAL
