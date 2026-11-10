from engine.knowledge_base import cargar_base_conocimiento, criterio_por_id
from engine.recognition.text import (
    alternativas,
    comparte_distintivo,
    consulta_semantica,
    normalizar,
    tokens,
)


def test_normalizar_quita_tildes_y_puntuacion():
    assert normalizar("Anticipo del 40% — Valor TOTAL.") == "anticipo del 40% valor total"


def test_alternativas_expande_y_descarta_numericos():
    assert alternativas([
        "anticipo / pago inicial / abono inicial", "40%", "0,40",
    ]) == ["anticipo", "pago inicial", "abono inicial"]


def test_tokens_quita_vacias_y_aplica_raiz():
    resultado = tokens("El anticipo se amortizara contra entregas parciales")
    assert "el" not in resultado
    assert "se" not in resultado
    assert "anticip" in resultado
    assert "entreg" in resultado


def test_consulta_semantica_incluye_queries_requisito_y_conceptos():
    criterio = criterio_por_id(cargar_base_conocimiento(), "GC-02")
    subrequisito = criterio["subrequisitos"][0]
    consulta = normalizar(consulta_semantica(subrequisito, criterio))
    assert "condiciones economicas" in consulta
    assert "anticipo equivalente al 40% del valor total" in consulta
    assert "pago inicial" in consulta


def test_comparte_distintivo_ignora_genericos():
    assert comparte_distintivo("credito comercial", "Credito aprobado por cartera")
    assert not comparte_distintivo("credito comercial", "Estado: Por Aprobacion")
    assert comparte_distintivo(
        "saldo contra entrega", "El saldo se paga contra entrega del suministro"
    )
