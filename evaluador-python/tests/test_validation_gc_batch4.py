import pytest

from engine.document_reader import leer_texto
from engine.knowledge_base import cargar_base_conocimiento
from engine.recognition import reconocer_documento
from engine.schema import (
    ESTADO_CUMPLE,
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


def test_gc20_gestion_polizas_completa(base):
    resultado = _validar(
        base,
        "GC-20",
        "Se solicita firma de polizas a gerencia; se evidencian polizas firmadas, "
        "digitalizadas y archivadas en bitacora con nomenclatura que identifica "
        "asesor, constructora, obra, contrato y polizas.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-20.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-20.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-20.3"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-20.4"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-20.5"]["estado"] == ESTADO_CUMPLE


def test_gc20_solo_polizas_es_parcial(base):
    resultado = _validar(base, "GC-20", "Se mencionan polizas.")
    assert resultado["estado"] == ESTADO_PARCIAL


def test_gc20_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-20", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc21_entrega_completa(base):
    resultado = _validar(
        base,
        "GC-21",
        "Se realiza entrega fisica y envio por correo electronico del contrato "
        "firmado en dos ejemplares, polizas firmadas, cuenta de cobro del anticipo "
        "y carta de envio de documentos.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-21.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-21.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-21.3"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-21.4"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-21.5"]["estado"] == ESTADO_CUMPLE


def test_gc21_solo_entrega_fisica_es_parcial(base):
    resultado = _validar(base, "GC-21", "Se realiza entrega fisica.")
    assert resultado["estado"] == ESTADO_PARCIAL
    subs = _subrequisitos(resultado)
    assert subs["GC-21.1"]["estado"] == ESTADO_PARCIAL


def test_gc21_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-21", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc22_entrega_cedi_completa(base):
    resultado = _validar(
        base,
        "GC-22",
        "Se realiza entrega fisica en el cedi con firma del jefe de cedi en el "
        "formato de entrega y acuse de recibo.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-22.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-22.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-22.3"]["estado"] == ESTADO_CUMPLE


def test_gc22_solo_entrega_fisica_es_parcial(base):
    resultado = _validar(base, "GC-22", "Se realiza entrega fisica.")
    assert resultado["estado"] == ESTADO_PARCIAL


def test_gc22_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-22", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc23_custodia_completa(base):
    resultado = _validar(
        base,
        "GC-23",
        "Se obtiene el contrato firmado por la obra, se entrega la documentacion "
        "fisica completa al area administrativa, que asume la custodia, control y "
        "archivo.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-23.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-23.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-23.3"]["estado"] == ESTADO_CUMPLE


def test_gc23_solo_contrato_firmado_es_parcial(base):
    resultado = _validar(base, "GC-23", "Contrato firmado.")
    assert resultado["estado"] == ESTADO_PARCIAL


def test_gc23_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-23", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc25_anexo_completo(base):
    resultado = _validar(
        base,
        "GC-25",
        "Se anexa garantia de interdoors como anexo de garantia que forma parte "
        "integral del contrato.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-25.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-25.2"]["estado"] == ESTADO_CUMPLE


def test_gc25_solo_garantia_es_parcial(base):
    resultado = _validar(base, "GC-25", "Se menciona garantia.")
    assert resultado["estado"] == ESTADO_PARCIAL


def test_gc25_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-25", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
