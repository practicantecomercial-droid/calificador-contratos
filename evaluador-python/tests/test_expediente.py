from docx import Document

from engine.document_reader import leer_texto
from engine.expediente import combinar_resultados, evaluar_expediente
from engine.pipeline import evaluar_documento_con_expediente
from engine.schema import (
    ALCANCE_EXPEDIENTE,
    ESTADO_CUMPLE,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
)


def _docx(ruta, texto=""):
    documento = Document()
    for linea in texto.splitlines():
        documento.add_paragraph(linea)
    documento.save(ruta)


def _resultados(reporte):
    return reporte["resultados"]


def test_expediente_completo_confirma_evidencia(tmp_path):
    _docx(
        tmp_path / "cotizaciones.docx",
        "Se anexan dos copias de los contratos.\n"
        "Cotizaciones firmadas y actualizadas.\n"
        "Firma previa del director comercial.",
    )
    _docx(
        tmp_path / "comprobante.docx",
        "Comprobante de pago del anticipo.\nEstado del pedido: generado.",
    )
    _docx(
        tmp_path / "anexo.docx",
        "Anexo de garantía de INTERDOORS.",
    )

    reporte = evaluar_expediente(tmp_path)
    resultados = _resultados(reporte)

    assert resultados["GC-16"]["estado"] == ESTADO_CUMPLE
    assert resultados["GC-24"]["estado"] == ESTADO_CUMPLE
    assert resultados["GC-25"]["estado"] == ESTADO_CUMPLE
    assert resultados["GC-16"]["alcance"] == ALCANCE_EXPEDIENTE
    assert resultados["GC-16"]["confianza"] == 1.0


def test_expediente_parcial_lista_evidencia_faltante(tmp_path):
    _docx(tmp_path / "cotizacion.docx", "Cotizaciones firmadas y actualizadas.")

    resultados = _resultados(evaluar_expediente(tmp_path))
    gc16 = resultados["GC-16"]

    assert gc16["estado"] == ESTADO_PARCIAL
    assert gc16["requiere_revision_humana"] is True
    assert "Evidencia externa: dos copias" in gc16["informacion_faltante"]
    assert (
        "Evidencia externa: firma previa del director comercial"
        in gc16["informacion_faltante"]
    )


def test_expediente_usa_nombres_de_archivo(tmp_path):
    _docx(tmp_path / "POLIZA FIRMADA.docx")
    _docx(tmp_path / "BITACORA.docx")

    resultados = _resultados(evaluar_expediente(tmp_path))
    assert resultados["GC-20"]["estado"] == ESTADO_CUMPLE


def test_expediente_vacio_no_identifica(tmp_path):
    resultados = _resultados(evaluar_expediente(tmp_path))
    assert resultados["GC-16"]["estado"] == ESTADO_NO_IDENTIFICADO
    assert resultados["GC-16"]["requiere_revision_humana"] is True


def test_pipeline_confirma_gc16_con_expediente(tmp_path):
    _docx(
        tmp_path / "soportes.docx",
        "Dos copias de los documentos del contrato.\n"
        "Cotizaciones firmadas y actualizadas.\n"
        "Firma previa del director comercial.",
    )

    reporte = evaluar_documento_con_expediente(
        leer_texto("Suministro de puertas de madera."),
        tmp_path,
        criterios=["GC-16"],
    )
    gc16 = reporte["resultados"]["GC-16"]

    assert gc16["estado"] == ESTADO_CUMPLE
    assert gc16["alcance"] == ALCANCE_EXPEDIENTE
    assert gc16["requiere_revision_humana"] is False
    assert gc16["resultado_documental"]["estado"] == ESTADO_NO_IDENTIFICADO
    assert gc16["resultado_expediente"]["estado"] == ESTADO_CUMPLE
    assert gc16["informacion_faltante"] == []
    assert reporte["resumen"]["evidencia_externa_pendiente"] == []


def test_conflicto_entre_contrato_y_expediente_requiere_revision():
    documental = {
        "GC-16": {
            "estado": ESTADO_NO_CUMPLE,
            "confianza": 0.9,
            "evidencia": [],
            "informacion_faltante": [],
            "observacion": "El contrato contradice el requisito.",
        }
    }
    expediente = {
        "GC-16": {
            "estado": ESTADO_CUMPLE,
            "confianza": 1.0,
            "evidencia": [{"archivo": "soportes.docx"}],
            "informacion_faltante": [],
            "observacion": "Evidencia completa.",
        }
    }

    combinado = combinar_resultados(documental, expediente)["GC-16"]

    assert combinado["estado"] == ESTADO_REVISION_HUMANA
    assert combinado["alcance"] == ALCANCE_EXPEDIENTE
    assert combinado["requiere_revision_humana"] is True
    assert combinado["resultado_documental"]["estado"] == ESTADO_NO_CUMPLE
