from engine.validation.operators import (
    clasificar_score,
    contiene_frase,
    contiene_porcentaje,
    numeros,
    porcentajes,
)


def test_numeros_tolera_miles_y_decimales():
    assert numeros("17,746,429.54") == [17746429.54]
    assert numeros("0,40") == [0.4]
    assert numeros("sin cifras") == []


def test_porcentajes_numericos_y_escritos():
    assert porcentajes("anticipo del 40% y saldo del 60%") == [40.0, 60.0]
    assert porcentajes("cuarenta por ciento del valor") == [40.0]


def test_contiene_porcentaje_acepta_fraccion_decimal():
    assert contiene_porcentaje("anticipo de 0,40 del valor total", 40) is True
    assert contiene_porcentaje("anticipo del 30%", 40) is False


def test_contiene_frase_normaliza_tildes_y_mayusculas():
    assert contiene_frase("Se pagará CONTRA ENTREGA", ("contra entrega",)) is True
    assert contiene_frase("Se pagará contra factura", ("contra entrega",)) is False


def test_clasificar_score_usa_umbrales():
    assert clasificar_score(0.90) == "alta"
    assert clasificar_score(0.75) == "probable"
    assert clasificar_score(0.55) == "debil"
    assert clasificar_score(0.20) == "nula"
