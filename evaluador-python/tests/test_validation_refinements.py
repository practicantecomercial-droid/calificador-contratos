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
from engine.validation.common import vigencia_meses


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


def test_vigencia_meses_interpreta_rangos_de_fechas():
    assert (
        vigencia_meses(
            "desde 30 de abril de 2026 hasta el 30 de abril de 2028"
        )
        == 24
    )
    assert (
        vigencia_meses("desde marzo 04 de 2026 hasta junio 30 de 2026")
        == 3
    )


def test_gc04_tiempo_de_entrega_no_sugiere_modalidad(base):
    resultado = _validar(
        base,
        "GC-04",
        "SUMINISTRO DE PUERTAS. EL TIEMPO DE ENTREGA SERAN 30 DIAS "
        "CALENDARIO COMO MAXIMO.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-04.2"]["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc05_mencion_de_obra_no_sugiere_recepcion(base):
    resultado = _validar(
        base,
        "GC-05",
        "SUMINISTRO DE PUERTAS PARA ZONAS COMUNES DE LA OBRA.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-05.3"]["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc06_vigencia_de_entrega_no_es_vigencia_de_cotizacion(base):
    resultado = _validar(
        base,
        "GC-06",
        "EL TIEMPO DE ENTREGA SERAN 30 DIAS CALENDARIO COMO MAXIMO.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-06.3"]["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc14_vigencia_con_rango_de_fechas_cumple(base):
    resultado = _validar(
        base,
        "GC-14",
        "GARANTIAS Y SEGUROS: CALIDAD DEL MATERIALES desde 30 de abril de "
        "2026 hasta el 30 de abril de 2028.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-14.3"]["estado"] == ESTADO_CUMPLE


def test_gc07_poliza_sin_cotizacion_no_es_parcial(base):
    resultado = _validar(
        base,
        "GC-07",
        "GARANTIAS Y SEGUROS: POLIZA DE CALIDAD DEL MATERIALES.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-07.3"]["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc13_pelikano_no_sugiere_vigencia_posterior(base):
    resultado = _validar(
        base,
        "GC-13",
        "SUMINISTRO DE PUERTAS COLOR ARTIKO PORO DE PELIKANO.",
    )
    assert resultado["estado"] == ESTADO_NO_APLICA


def test_gc10_descripcion_no_sugiere_indice_de_precios(base):
    resultado = _validar(
        base,
        "GC-10",
        "Descripcion: SUMINISTRO DE PUERTAS CARPINTERIA MADERA.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-10.2"]["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc18_etiqueta_otrosi_vacia_no_es_parcial(base):
    resultado = _validar(
        base,
        "GC-18",
        "Otrosi Contrato: Fecha Inicio: 04/03/2026.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-18.2"]["estado"] == ESTADO_NO_APLICA


def test_gc19_mencion_de_poliza_no_sugiere_solicitud(base):
    resultado = _validar(
        base,
        "GC-19",
        "GARANTIAS Y SEGUROS: POLIZA DE CALIDAD DEL MATERIALES.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-19.3"]["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc20_mencion_de_poliza_no_sugiere_firma(base):
    resultado = _validar(
        base,
        "GC-20",
        "GARANTIAS Y SEGUROS: POLIZA DE CALIDAD DEL MATERIALES.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-20.2"]["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc21_mencion_de_poliza_no_sugiere_entrega(base):
    resultado = _validar(
        base,
        "GC-21",
        "GARANTIAS Y SEGUROS: POLIZA DE CALIDAD DEL MATERIALES.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-21.3"]["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc25_mencion_de_garantia_no_sugiere_anexo(base):
    resultado = _validar(
        base,
        "GC-25",
        "GARANTIAS Y SEGUROS: POLIZA DE CALIDAD DEL MATERIALES.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-25.1"]["estado"] == ESTADO_NO_IDENTIFICADO


def test_gc19_solicitud_de_anticipo_sin_cuenta_es_parcial(base):
    resultado = _validar(base, "GC-19", "Se solicita anticipo.")
    subs = _subrequisitos(resultado)
    assert subs["GC-19.2"]["estado"] == ESTADO_PARCIAL
