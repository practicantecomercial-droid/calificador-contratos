"""Interfaz Streamlit del evaluador documental."""
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from core.ai_analyzer import analyze_with_ai, api_key_disponible
from core.document_loader import load_document
from core.rule_engine import evaluar_checklist, load_checklist
from core.scoring import build_summary
from reports.excel_report import export_results_to_excel
from reports.pdf_report import generate_evaluation_pdf

st.set_page_config(page_title="Evaluador de Contratos — Interdoors", layout="wide")

ESTADO_COLOR = {"cumple": "green", "parcial": "orange", "no_cumple": "red"}


def enriquecer(resultados, criterios):
    by_id = {c["id"]: c for c in criterios}
    for r in resultados:
        c = by_id.get(r["criterio_id"], {})
        r.setdefault("nombre", c.get("nombre", ""))
        r.setdefault("peso", c.get("peso", 1))
        r.setdefault("critico", c.get("critico", False))
        r.setdefault("categoria", c.get("categoria", ""))
    return resultados


st.title("Evaluador de Contratos — Interdoors")
st.caption("Lista de chequeo de gestión de contratos (25 criterios) · OCR + reglas locales · IA opcional")

# ── A. Cargar documento ──────────────────────────────────────────────────────
uploaded = st.file_uploader("Cargar contrato", type=["pdf", "docx", "png", "jpg", "jpeg"])
modo = st.radio("Modo de evaluación", ["Reglas locales", "IA (OpenAI)", "Ambas"], horizontal=True)

if uploaded is None:
    st.info("Sube un contrato (PDF, Word o imagen escaneada) para comenzar.")
    st.stop()

sufijo = Path(uploaded.name).suffix or ".pdf"
with tempfile.NamedTemporaryFile(delete=False, suffix=sufijo) as tmp:
    tmp.write(uploaded.getbuffer())
    tmp_path = tmp.name

try:
    doc = load_document(tmp_path)
except ValueError as e:
    st.error(str(e))
    st.stop()

texto = doc["texto"]
criterios = load_checklist()

# ── B. Revisar extracción ────────────────────────────────────────────────────
with st.expander("Revisar extracción", expanded=False):
    paginas_ocr = [p for p in doc["paginas"] if p.get("ocr")]
    st.write(f"{len(texto)} caracteres · {len(doc['paginas'])} páginas · {len(paginas_ocr)} con OCR")
    if paginas_ocr:
        st.warning("Algunas páginas se leyeron con OCR; revisa que el texto sea correcto.")
    st.text_area("Texto extraído", texto, height=200)

# ── C. Evaluación ────────────────────────────────────────────────────────────
st.subheader("Evaluación de criterios")

resultados = None
if modo == "Reglas locales":
    resultados = evaluar_checklist(texto, criterios)
elif modo == "IA (OpenAI)":
    if not api_key_disponible():
        st.error("Falta OPENAI_API_KEY. Configúrala como variable de entorno o en un archivo .env")
        st.stop()
    try:
        with st.spinner("Analizando con IA…"):
            resultados = enriquecer(analyze_with_ai(texto, criterios), criterios)
    except Exception as e:
        st.error(str(e))
        st.stop()
else:  # Ambas
    resultados = evaluar_checklist(texto, criterios)
    if api_key_disponible():
        try:
            with st.spinner("Comparando con IA…"):
                ia = enriquecer(analyze_with_ai(texto, criterios), criterios)
                st.session_state["resultados_ia"] = ia
        except Exception as e:
            st.warning(f"No se pudo consultar la IA: {e}")

summary = build_summary(resultados)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Puntaje", f"{summary['puntaje']}%")
col2.metric("Cumple", summary["estados"]["cumple"])
col3.metric("Parcial", summary["estados"]["parcial"])
col4.metric("No cumple", summary["estados"]["no_cumple"])

if not summary["apto"]:
    st.error("NO APTO — criterios críticos fallidos: " + ", ".join(summary["criticos_fallidos"]))
else:
    st.success("APTO")

for r in resultados:
    color = ESTADO_COLOR[r["estado"]]
    marca = "CRÍTICO" if r.get("critico") else ""
    st.markdown(
        f":{color}[**{r['estado'].upper()}**] **{r['criterio_id']}. {r['nombre']}** "
        f"({r.get('cobertura', '')}) {marca}"
    )
    st.markdown(f"<small>{r['justificacion']}</small>", unsafe_allow_html=True)
    st.divider()

if "resultados_ia" in st.session_state:
    with st.expander("Resultado de IA (comparación)"):
        for r in st.session_state["resultados_ia"]:
            color = ESTADO_COLOR[r["estado"]]
            st.markdown(f":{color}[**{r['estado'].upper()}**] {r['criterio_id']}. {r['nombre']} — {r['justificacion']}")

# ── D. Exportar ──────────────────────────────────────────────────────────────
st.subheader("Exportar informe")
col1, col2 = st.columns(2)
with col1:
    if st.button("Exportar Excel"):
        path = export_results_to_excel(resultados, summary)
        st.success(f"Generado: {path}")
with col2:
    if st.button("Exportar PDF"):
        path = generate_evaluation_pdf(resultados, summary)
        st.success(f"Generado: {path}")
