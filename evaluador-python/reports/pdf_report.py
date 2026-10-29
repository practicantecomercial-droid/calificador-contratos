"""Genera un informe PDF con los resultados de la evaluación."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config import REPORTS_DIR

ESTADO_COLOR = {
    "cumple": colors.HexColor("#15803d"),
    "parcial": colors.HexColor("#b45309"),
    "no_cumple": colors.HexColor("#dc2626"),
}


def generate_evaluation_pdf(resultados, summary=None, output_path=None):
    if output_path is None:
        output_path = REPORTS_DIR / "evaluacion.pdf"

    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle("Titulo", parent=styles["Title"], fontSize=16)
    estado = ParagraphStyle("Estado", parent=styles["Normal"], fontSize=10)

    story = [Paragraph("Reporte de Evaluación de Contrato", titulo)]
    if summary:
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"Puntaje: <b>{summary['puntaje']}%</b> — "
            f"Cumple: {summary['estados']['cumple']}, "
            f"Parcial: {summary['estados']['parcial']}, "
            f"No cumple: {summary['estados']['no_cumple']} — "
            f"{'APTO' if summary['apto'] else 'NO APTO'}",
            estado,
        ))
    story.append(Spacer(1, 12))

    data = [["#", "Criterio", "Estado", "Justificación"]]
    for r in resultados:
        data.append([
            str(r["criterio_id"]),
            Paragraph(r["nombre"], estado),
            r["estado"].upper(),
            Paragraph(r["justificacion"], estado),
        ])

    tabla = Table(data, colWidths=[24, 180, 70, 240])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2430")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e4e8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(tabla)

    doc.build(story)
    return str(output_path)
