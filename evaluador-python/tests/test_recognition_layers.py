from engine.recognition import contextual, lexical, literal, semantic


def test_literal_frase_exacta():
    resultados = literal.buscar(
        "El saldo se pagara contra entrega del suministro.", ["contra entrega"]
    )
    assert resultados[0]["termino"] == "contra entrega"
    assert resultados[0]["score"] == 1.0


def test_literal_coincidencia_parcial():
    resultados = literal.buscar(
        "Se pagara el monto total acordado.", ["monto total del contrato"]
    )
    assert resultados
    assert 0.6 <= resultados[0]["score"] < 1.0


def test_literal_sin_coincidencia():
    assert literal.buscar(
        "El plazo sera de treinta dias.", ["poliza de cumplimiento"]
    ) == []


def test_lexical_reconoce_sinonimo():
    score, termino = lexical.puntuar(
        "Se otorgara un abono inicial del cuarenta por ciento.",
        ["anticipo / pago inicial / abono inicial", "cuarenta por ciento"],
    )
    assert score >= 0.9
    assert termino in {"abono inicial", "cuarenta por ciento"}


def test_lexical_descarta_solapamiento_solo_generico():
    score, termino = lexical.puntuar(
        "El tiempo de entrega sera de treinta dias.",
        ["valor restante", "al entregar"],
    )
    assert score == 0.0
    assert termino is None


def test_semantic_ordena_unidad_relevante():
    textos = [
        "El contratante pagara un anticipo del cuarenta por ciento.",
        "El saldo se facturara contra entrega del suministro.",
        "La poliza de cumplimiento tendra una vigencia de un ano.",
    ]
    indice = semantic.IndiceBM25(textos)
    mejores = indice.mejores(
        "saldo contra entrega del suministro", top_k=3, umbral=0.0
    )
    assert mejores
    assert mejores[0][0] == 1


def test_semantic_normaliza_entre_cero_y_uno():
    indice = semantic.IndiceBM25(["anticipo del cuarenta por ciento"])
    mejores = indice.mejores("anticipo", top_k=1, umbral=0.0)
    assert mejores
    posicion, score = mejores[0]
    assert posicion == 0
    assert 0.0 < score <= 1.0


def test_semantic_corpus_vacio():
    indice = semantic.IndiceBM25([])
    assert indice.mejores("anticipo", top_k=3, umbral=0.0) == []


def test_contextual_detecta_negacion():
    subrequisito = {"texto": "Bilateralidad de la terminacion"}
    analisis = contextual.analizar(
        "No se reconocera terminacion unilateral.", "terminacion", subrequisito
    )
    assert analisis["flags"]["negado"] is True
    assert analisis["ajuste"] < 1.0


def test_contextual_detecta_retencion_de_anticipo():
    subrequisito = {"texto": "Anticipo equivalente al 40% del valor total"}
    analisis = contextual.analizar("Ret Anticipo: 30 %", "anticipo", subrequisito)
    assert analisis["flags"]["es_retencion"] is True
    assert "retencion_no_es_anticipo" in analisis["contradicciones"]
    assert analisis["ajuste"] <= 0.3


def test_contextual_detecta_evento_distinto():
    subrequisito = {
        "texto": "Saldo del 60% facturado contra entrega del suministro"
    }
    analisis = contextual.analizar(
        "El saldo se pagara contra instalacion.", "saldo", subrequisito
    )
    assert "evento_distinto" in analisis["contradicciones"]
    assert analisis["ajuste"] < 1.0


def test_contextual_identifica_sujeto():
    subrequisito = {"texto": "Anticipo equivalente al 40% del valor total"}
    analisis = contextual.analizar(
        "El contratante pagara un anticipo del 40%.", "anticipo", subrequisito
    )
    assert analisis["flags"]["sujeto"] == "contratante"


def test_reordenar_con_llm_sin_clave_no_cambia(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    candidatos = [{"texto": "primero"}, {"texto": "segundo"}]
    assert semantic.reordenar_con_llm("consulta", candidatos) == candidatos
