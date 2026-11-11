import pytest

from engine.document_reader import leer_texto
from engine.knowledge_base import cargar_base_conocimiento
from engine.recognition import reconocer_documento
from engine.schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
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


def test_gc13_vigencia_posterior_con_reajuste(base):
    resultado = _validar(
        base,
        "GC-13",
        "La ejecucion se realizara en el ano siguiente y se preve solicitud de "
        "reajuste conforme al mercado.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-13.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-13.2"]["estado"] == ESTADO_CUMPLE


def test_gc13_sin_vigencia_posterior_no_aplica(base):
    resultado = _validar(base, "GC-13", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_APLICA


def test_gc13_vigencia_sin_reajuste_es_parcial(base):
    resultado = _validar(
        base, "GC-13", "La ejecucion se realizara en vigencia posterior."
    )
    assert resultado["estado"] == ESTADO_PARCIAL


def test_gc15_revision_firma_y_gerencia(base):
    resultado = _validar(
        base,
        "GC-15",
        "Contrato revisado por el director comercial, firmado por el director "
        "comercial y remitido a gerencia para aprobacion final.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-15.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-15.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-15.3"]["estado"] == ESTADO_CUMPLE


def test_gc15_solo_revision_es_parcial(base):
    resultado = _validar(
        base, "GC-15", "Revision del director comercial."
    )
    assert resultado["estado"] == ESTADO_PARCIAL


def test_gc15_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-15", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc17_gestion_documental_completa(base):
    resultado = _validar(
        base,
        "GC-17",
        "Los documentos firmados se digitalizan y se archivan en la carpeta "
        "bitacora con nomenclatura que incluye asesor, constructora y obra.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-17.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-17.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-17.3"]["estado"] == ESTADO_CUMPLE


def test_gc17_solo_firmados_es_parcial(base):
    resultado = _validar(
        base, "GC-17", "Los documentos firmados se entregan."
    )
    assert resultado["estado"] == ESTADO_PARCIAL


def test_gc17_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-17", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc18_registro_completo(base):
    resultado = _validar(
        base,
        "GC-18",
        "El contrato se registra en la relacion de contratos, con fecha de inicio "
        "del tramite, firma del gerente general y actualizacion los dias 15 y 30 "
        "de cada mes.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-18.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-18.2"]["estado"] == ESTADO_NO_APLICA
    assert subs["GC-18.3"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-18.4"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-18.5"]["estado"] == ESTADO_CUMPLE


def test_gc18_otrosi_sin_actualizacion_es_parcial(base):
    resultado = _validar(base, "GC-18", "Se firma otrosi.")
    subs = _subrequisitos(resultado)
    assert subs["GC-18.2"]["estado"] == ESTADO_PARCIAL


def test_gc18_otrosi_con_actualizacion_cumple(base):
    resultado = _validar(
        base, "GC-18", "Se firma otrosi con actualizacion del plazo."
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-18.2"]["estado"] == ESTADO_CUMPLE


def test_gc18_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-18", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc19_solicitud_completa(base):
    resultado = _validar(
        base,
        "GC-19",
        "Se envia correo al analista de cartera y jefe administrativo solicitando "
        "cuenta de cobro del anticipo y solicitud de polizas requeridas, con "
        "mencion de la aseguradora, y se archiva en bitacora junto con el contrato.",
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    subs = _subrequisitos(resultado)
    assert subs["GC-19.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-19.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-19.3"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-19.4"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-19.5"]["estado"] == ESTADO_CUMPLE


def test_gc19_solo_anticipo_es_parcial(base):
    resultado = _validar(base, "GC-19", "Se solicita anticipo.")
    assert resultado["estado"] == ESTADO_PARCIAL
    subs = _subrequisitos(resultado)
    assert subs["GC-19.2"]["estado"] == ESTADO_PARCIAL


def test_gc19_sin_mencion_no_identifica(base):
    resultado = _validar(base, "GC-19", "Suministro de puertas.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
