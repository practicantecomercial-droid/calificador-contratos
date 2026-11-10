import json

from docx import Document

import cli
from engine.schema import ESTADO_CUMPLE

TEXTO = (
    "CLÁUSULA PRIMERA. FORMA DE PAGO\n"
    "El contratante pagará un anticipo equivalente al 40% del valor total "
    "del contrato. El saldo del 60% se facturará contra entrega del suministro."
)


def _crear_docx(ruta):
    documento = Document()
    for linea in TEXTO.splitlines():
        documento.add_paragraph(linea)
    documento.save(ruta)


def test_cli_imprime_resumen(tmp_path, capsys):
    ruta = tmp_path / "contrato.docx"
    _crear_docx(ruta)

    codigo = cli.main([str(ruta), "--criterios", "GC-02"])
    salida = capsys.readouterr().out

    assert codigo == 0
    assert "GC-02" in salida
    assert "CUMPLE" in salida
    assert "Puntaje:" in salida


def test_cli_json_es_parseable(tmp_path, capsys):
    ruta = tmp_path / "contrato.docx"
    _crear_docx(ruta)

    codigo = cli.main([str(ruta), "--criterios", "GC-02", "--json"])
    reporte = json.loads(capsys.readouterr().out)

    assert codigo == 0
    assert reporte["resultados"]["GC-02"]["estado"] == ESTADO_CUMPLE


def test_cli_archivo_inexistente(capsys):
    codigo = cli.main(["no-existe.pdf"])
    assert codigo == 2
    assert "No existe" in capsys.readouterr().err
