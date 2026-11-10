from pathlib import Path

import pytest

from engine.document_reader import leer_documento, leer_texto
from engine.knowledge_base import cargar_base_conocimiento
from engine.recognition import reconocer_documento
from engine.schema import (
    ALCANCE_EVIDENCIA_EXTERNA,
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
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
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-24"])
    return validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-24"]
    )["criterios"]["GC-24"]


def _subrequisitos(resultado):
    return {
        subrequisito["subrequisito_id"]: subrequisito
        for subrequisito in resultado["subrequisitos"]
    }


def test_control_de_anticipo_completo_cumple(base):
    resultado = _validar(
        base,
        "Anticipo pagado y comprobante de pago - "
        "Generación de pedido y fabricación - "
        "El envío a fabricación queda bloqueado hasta confirmar el abono - "
        "Gestión del anticipo por el asesor comercial.",
    )
    subs = _subrequisitos(resultado)
    assert resultado["estado"] == ESTADO_CUMPLE
    assert subs["GC-24.1"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-24.2"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-24.3"]["estado"] == ESTADO_CUMPLE
    assert subs["GC-24.4"]["estado"] == ESTADO_NO_APLICA


def test_solo_anticipo_mencionado_no_identifica(base):
    resultado = _validar(base, "El cliente pagará un anticipo del 30%.")
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultado["alcance"] == ALCANCE_EVIDENCIA_EXTERNA
    assert resultado["requiere_revision_humana"] is True


def test_excepcion_sin_autorizacion_requiere_revision(base):
    resultado = _validar(base, "Excepción al control del anticipo.")
    subs = _subrequisitos(resultado)
    assert subs["GC-24.4"]["estado"] == ESTADO_REVISION_HUMANA
    assert resultado["requiere_revision_humana"] is True


def test_excepcion_autorizada_cumple(base):
    resultado = _validar(
        base, "Excepción al control del anticipo aprobada por el director comercial."
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-24.4"]["estado"] == ESTADO_CUMPLE


def test_pedido_sin_bloqueo_de_fabricacion_es_parcial(base):
    resultado = _validar(
        base,
        "Generación de pedido y fabricación del producto.",
    )
    subs = _subrequisitos(resultado)
    assert subs["GC-24.2"]["estado"] == ESTADO_PARCIAL


@pytest.mark.skipif(not PDF_2780477.exists(), reason="PDF de prueba no disponible")
def test_pdf_real_sin_control_de_anticipo(base):
    documento = leer_documento(PDF_2780477)
    reconocimiento = reconocer_documento(base, documento, criterios=["GC-24"])
    resultado = validar_documento(
        base, reconocimiento, documento=documento, criterios=["GC-24"]
    )["criterios"]["GC-24"]

    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultado["alcance"] == ALCANCE_EVIDENCIA_EXTERNA
    assert "Comprobante de pago o confirmación del abono y estado del pedido" in (
        resultado["informacion_faltante"]
    )
    assert resultado["requiere_revision_humana"] is True
