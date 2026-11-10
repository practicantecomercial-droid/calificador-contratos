from engine.document_reader import leer_texto
from engine.segmenter import segmentar, unidades_por_tipo


def test_genera_unidades_de_campo(documento_erp):
    campos = unidades_por_tipo(segmentar(documento_erp), "campo")
    assert campos
    tipo = next(unidad for unidad in campos if unidad["clave"] == "tipo contrato")
    assert tipo["texto"] == "Tipo Contrato: SUMINISTRO DE MATERIALES OBRA"
    assert tipo["pagina"] == 1
    assert tipo["lineas"]


def test_genera_parrafos(documento_erp):
    parrafos = unidades_por_tipo(segmentar(documento_erp), "parrafo")
    assert parrafos
    assert any("CONSTRUCCIONES BUEN VIVIR" in p["texto"] for p in parrafos)


def test_detecta_clausulas_en_prosa():
    documento = leer_texto(
        "CLÁUSULA PRIMERA. OBJETO\n"
        "El objeto es el suministro de puertas.\n\n"
        "CLÁUSULA SEGUNDA. VALOR\n"
        "El valor es de 100."
    )
    clausulas = unidades_por_tipo(segmentar(documento), "clausula")
    assert len(clausulas) == 2
    assert "OBJETO" in clausulas[0]["titulo"]
    assert "VALOR" in clausulas[1]["titulo"]
    assert "suministro de puertas" in clausulas[0]["texto"]


def test_ids_unicos(documento_erp):
    unidades = segmentar(documento_erp)
    assert len({unidad["id"] for unidad in unidades}) == len(unidades)
    assert all(unidad["tipo"] in {"campo", "parrafo", "clausula"} for unidad in unidades)
