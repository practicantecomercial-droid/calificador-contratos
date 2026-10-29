from core import text_cleaner as tc


def test_normalize_text_quita_tildes_y_mayusculas():
    assert tc.normalize_text("PÓLIZA DE CUMPLIMIENTO") == "poliza de cumplimiento"
    assert tc.normalize_text("GESTIÓN") == "gestion"


def test_extract_percentages_digitos_y_letras():
    r = tc.extract_percentages("anticipo 40% y cuarenta por ciento. Ret Anticipo 30%")
    assert 40 in r
    assert 30 in r


def test_extract_durations_digitos_y_letras():
    p = tc.extract_durations("vigencia mínima de tres (3) años y 30 dias de credito")
    assert any(x["valor"] == 3 and x["unidad"] == "años" for x in p)
    assert any(x["valor"] == 30 and x["unidad"] == "dias" for x in p)


def test_normalize_unit():
    assert tc.normalize_unit("años") == "años"
    assert tc.normalize_unit("anos") == "años"
    assert tc.normalize_unit("dias") == "dias"
    assert tc.normalize_unit("meses") == "meses"


def test_stem():
    assert tc.stem("firmada") == tc.stem("firma")
    assert tc.stem("escaneados") == tc.stem("escaneado")
