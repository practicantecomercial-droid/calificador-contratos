from pathlib import Path

import pytest

from engine.document_reader import leer_texto
from engine.knowledge_base import cargar_base_conocimiento
from engine.recognition import reconocer_documento
from engine.schema import (
    ALCANCE_EVIDENCIA_EXTERNA,
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


def test_gc01_documentos_completos(base):
    resultado = _validar(
        base,
        "GC-01",
        "Se anexan dos copias del contrato - cotizacion firmada y actualizada - "
        "costeo detallado - manual del contratista - documentos de seguridad y "
        "salud en el trabajo - anexos con firma del coordinador sst - cliente "
        "constructora, se anexa carta de no siniestro.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-01.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-01.6"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-01.7"]["estado"] == ESTADO_CUMPLE


def test_gc01_sin_documentos_marca_externa(base):
    resultado = _validar(base, "GC-01", "Suministro de puertas de madera.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultado["alcance"] == ALCANCE_EVIDENCIA_EXTERNA
    assert resultado["requiere_revision_humana"] is True


def test_gc01_copias_sin_entrega_es_parcial(base):
    resultado = _validar(
        base, "GC-01", "Se requieren dos copias del contrato."
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-01.1"]["estado"] == ESTADO_PARCIAL


def test_gc01_constructora_sin_carta_es_parcial(base):
    resultado = _validar(
        base, "GC-01", "El cliente es una constructora."
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-01.7"]["estado"] == ESTADO_PARCIAL


def test_gc01_sin_anexos_es_no_aplica(base):
    resultado = _validar(base, "GC-01", "Suministro de puertas.")
    subs = _subrequisitos(resultado)
    assert subs["GC-01.6"]["estado"] == ESTADO_NO_APLICA
    assert subs["GC-01.7"]["estado"] == ESTADO_NO_APLICA


def test_gc03_servicios_independientes(base):
    resultado = _validar(
        base,
        "GC-03",
        "El suministro y la instalacion se ofrecen como servicios independientes "
        "y el pago del suministro no depende de la instalacion, con facturacion "
        "separada por concepto.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-03.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-03.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-03.3"]["estado"] == ESTADO_CUMPLE


def test_gc03_pago_condicionado_no_cumple(base):
    resultado = _validar(
        base,
        "GC-03",
        "El pago del suministro esta condicionado a la instalacion.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-03.2"]["estado"] == ESTADO_NO_CUMPLE
    assert resultado["estado"] == ESTADO_NO_CUMPLE


def test_gc03_sin_independencia_es_parcial(base):
    resultado = _validar(
        base, "GC-03", "Suministro e instalacion de puertas."
    )
    assert resultado["estado"] == ESTADO_PARCIAL


def test_gc04_facturacion_contra_entrega(base):
    resultado = _validar(
        base,
        "GC-04",
        "La facturacion del suministro se realizara contra entrega en obra, con "
        "entregas parciales segun lo acordado.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-04.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-04.2"]["estado"] == ESTADO_CUMPLE


def test_gc04_facturacion_sin_entrega_es_parcial(base):
    resultado = _validar(base, "GC-04", "Facturacion del suministro.")
    assert resultado["estado"] == ESTADO_PARCIAL
    subs = _subrequisitos(resultado)
    assert subs["GC-04.1"]["estado"] == ESTADO_PARCIAL


def test_gc05_cortes_semanales_completos(base):
    resultado = _validar(
        base,
        "GC-05",
        "La facturacion de la instalacion tendra cortes semanales basados en el "
        "avance efectivamente realizado, con disponibilidad de recepcion en obra.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-05.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-05.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-05.3"]["estado"] == ESTADO_CUMPLE


def test_gc05_sin_cortes_es_parcial(base):
    resultado = _validar(base, "GC-05", "Facturacion de la instalacion.")
    assert resultado["estado"] == ESTADO_PARCIAL
    subs = _subrequisitos(resultado)
    assert subs["GC-05.1"]["estado"] == ESTADO_PARCIAL


def test_gc06_cotizacion_completa(base):
    resultado = _validar(
        base,
        "GC-06",
        "La cotizacion mantiene correspondencia de precios y cantidades con el "
        "contrato, con vigencia de 30 dias calendario y verificacion de precios.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-06.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-06.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-06.3"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-06.4"]["estado"] == ESTADO_CUMPLE


def test_gc06_vigencia_sin_plazo_es_parcial(base):
    resultado = _validar(base, "GC-06", "La cotizacion tiene vigencia.")
    subs = _subrequisitos(resultado)
    assert subs["GC-06.3"]["estado"] == ESTADO_PARCIAL
