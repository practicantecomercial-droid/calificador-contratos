from core import scoring


def _r(estado, peso=10, critico=False, nombre=""):
    return {"estado": estado, "peso": peso, "critico": critico, "nombre": nombre, "categoria": "x"}


def test_calculate_score():
    resultados = [_r("cumple"), _r("parcial"), _r("no_cumple"), _r("cumple")]
    # pesos iguales 10 -> puntos = 10 + 5 + 0 + 10 = 25 sobre 40 = 62.5%
    assert scoring.calculate_score(resultados) == 62.5


def test_check_critical_failures():
    resultados = [_r("cumple", critico=True), _r("no_cumple", critico=True), _r("no_cumple", critico=False)]
    fallidos = scoring.check_critical_failures(resultados)
    assert len(fallidos) == 1


def test_build_summary_apto():
    resultados = [_r("cumple", critico=True), _r("parcial"), _r("cumple")]
    s = scoring.build_summary(resultados)
    assert s["apto"] is True
    assert s["estados"] == {"cumple": 2, "parcial": 1, "no_cumple": 0}
