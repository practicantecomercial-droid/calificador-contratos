from engine.schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
    nuevo_criterio,
    nuevo_subrequisito,
)
from engine.validation import validar_criterio
from engine.validation.generic import (
    calcular_confianza,
    combinar_estado,
    construir_resultado,
    validar_criterio_generico,
    validar_subrequisito_generico,
)


def _candidato(texto="Evidencia de prueba", score=1.0, capa="literal", **extra):
    candidato = {
        "criterio_id": "GC-99",
        "subrequisito_id": "GC-99.1",
        "unidad_id": "U0001",
        "tipo_unidad": "clausula",
        "texto": texto,
        "pagina": 1,
        "lineas": [1],
        "capa": capa,
        "termino": texto,
        "score_base": score,
        "score": score,
        "contexto": {},
        "contradicciones": [],
        "descartable_para_concepto": False,
    }
    candidato.update(extra)
    return candidato


def _criterio():
    subrequisito = nuevo_subrequisito(
        criterio_id="GC-99",
        indice=1,
        texto="Condición de prueba",
        conceptos=["condicion de prueba"],
    )
    return nuevo_criterio(
        criterio_id="GC-99",
        numero=99,
        nombre="Criterio de prueba",
        subrequisitos=[subrequisito],
    )


def _resultado(estado, score=0.9, evidencia=None, contradicciones=None):
    return {
        "subrequisito_id": "GC-99.1",
        "texto": "Condición de prueba",
        "estado": estado,
        "confianza": 0.9,
        "score": score,
        "evidencia": evidencia or [],
        "observacion": "",
        "contradicciones": contradicciones or [],
    }


def test_sin_candidatos_es_no_identificado():
    resultado = validar_subrequisito_generico(_criterio()["subrequisitos"][0], [])
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultado["confianza"] == 0.0


def test_literal_alto_es_cumple():
    candidato = _candidato()
    resultado = validar_subrequisito_generico(
        _criterio()["subrequisitos"][0], [candidato]
    )
    assert resultado["estado"] == ESTADO_CUMPLE
    assert resultado["evidencia"][0]["unidad_id"] == "U0001"


def test_candidato_descartable_se_ignora():
    candidato = _candidato(descartable_para_concepto=True)
    resultado = validar_subrequisito_generico(
        _criterio()["subrequisitos"][0], [candidato]
    )
    assert resultado["estado"] == ESTADO_NO_IDENTIFICADO


def test_contradiccion_exige_revision_humana():
    candidato = _candidato(contradicciones=["evento_distinto"])
    resultado = validar_subrequisito_generico(
        _criterio()["subrequisitos"][0], [candidato]
    )
    assert resultado["estado"] == ESTADO_REVISION_HUMANA


def test_combinar_estado_prioriza_no_cumple():
    estados = [
        _resultado(ESTADO_CUMPLE),
        _resultado(ESTADO_NO_CUMPLE),
        _resultado(ESTADO_NO_APLICA),
    ]
    assert combinar_estado(estados) == ESTADO_NO_CUMPLE


def test_combinar_estado_mixto_es_parcial():
    estados = [_resultado(ESTADO_CUMPLE), _resultado(ESTADO_NO_IDENTIFICADO)]
    assert combinar_estado(estados) == ESTADO_PARCIAL


def test_combinar_estado_solo_no_aplica():
    estados = [_resultado(ESTADO_NO_APLICA), _resultado(ESTADO_NO_APLICA)]
    assert combinar_estado(estados) == ESTADO_NO_APLICA


def test_confianza_penaliza_contradicciones():
    sin_contradiccion = calcular_confianza(
        [_resultado(ESTADO_CUMPLE, evidencia=[{"texto": "x"}])]
    )
    con_contradiccion = calcular_confianza(
        [
            _resultado(
                ESTADO_CUMPLE,
                evidencia=[{"texto": "x"}],
                contradicciones=["evento_distinto"],
            )
        ]
    )
    assert con_contradiccion < sin_contradiccion


def test_construir_resultado_reporta_forma_de_pago_vacia():
    criterio = _criterio()
    resultado = construir_resultado(
        criterio,
        [_resultado(ESTADO_NO_IDENTIFICADO, score=0.0)],
        ESTADO_NO_IDENTIFICADO,
        0.0,
        contexto={"forma_pago": {"vacia": True}},
    )
    assert "Forma de pago vacía en el contrato" in resultado["informacion_faltante"]
    assert resultado["requiere_revision_humana"] is True


def test_validar_criterio_generico_extremo_a_extremo():
    criterio = _criterio()
    reconocimiento = {
        "criterio_id": "GC-99",
        "subrequisitos": {"GC-99.1": [_candidato()]},
        "mejores": {"GC-99.1": _candidato()},
    }
    resultado = validar_criterio_generico(criterio, reconocimiento)
    assert resultado["estado"] == ESTADO_CUMPLE
    assert resultado["confianza"] >= 0.8


def test_validar_criterio_usa_generico_si_no_hay_regla():
    criterio = _criterio()
    reconocimiento = {
        "criterio_id": "GC-99",
        "subrequisitos": {"GC-99.1": [_candidato()]},
    }
    resultado = validar_criterio(criterio, reconocimiento)
    assert resultado["criterio_id"] == "GC-99"
    assert resultado["estado"] == ESTADO_CUMPLE
