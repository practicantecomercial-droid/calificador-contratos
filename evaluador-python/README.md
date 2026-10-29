# Evaluador Documental de Contratos — Interdoors

Aplicación **local en Python** para evaluar contratos de obra contra la lista de chequeo de gestión de contratos (25 criterios). Lee PDF (incluso escaneados, con OCR), Word e imágenes, y determina si cada criterio **cumple**, **parcial** o **no cumple**, con evidencia y puntaje ponderado. Incluye un modo de **IA opcional (OpenAI)**.

## Requisitos

- Python 3.11+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) instalado (para documentos escaneados)
  - El idioma español (`spa.traineddata`) ya viene incluido en `data/tessdata/`.

## Instalación

```bash
cd evaluador_interdoors
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python scripts\download_tessdata.py   # descarga los modelos de idioma para OCR
```

## Uso

### Interfaz web (Streamlit)
```bash
.venv\Scripts\streamlit run app.py
```
Abre http://localhost:8501. Sube el contrato, revisa la extracción, elige el modo de evaluación y exporta Excel/PDF.

### Línea de comandos
```bash
.venv\Scripts\python cli.py "ruta/contrato.pdf"
```

## Modos de evaluación

| Modo | Descripción |
|---|---|
| **Reglas locales** | Motor de reglas con sub-ítems, sinónimos, números, plazos y negación. Sin internet. |
| **IA (OpenAI)** | Análisis semántico con OpenAI. Requiere `OPENAI_API_KEY`. |
| **Ambas** | Reglas locales + comparación con IA. |

Para activar la IA, define la variable de entorno `OPENAI_API_KEY` (o crea un `.env` con esa clave).

## Cómo decide "cumple"

Cada criterio se descompone en **sub-ítems** (ver `rules/checklist.yaml`). Un sub-ítem se cumple si:
- aparece alguno de sus **términos** (con normalización de tildes, raíz y tolerancia a tipeos), y
- se cumple su **patrón** numérico (porcentajes o plazos, en dígitos o letras), y
- no hay **negación** cerca (`no`, `sin`, `unilateral`, …).

Luego:
- cumplidos ≥ `minimo_subitems` → **Cumple**
- 0 < cumplidos < mínimo → **Parcial**
- 0 → **No cumple**

## Estructura

```
evaluador_interdoors/
├── app.py                  # UI Streamlit
├── cli.py                  # Evaluación por terminal
├── config.py               # rutas, OCR, modelo IA
├── requirements.txt
├── core/
│   ├── document_loader.py
│   ├── pdf_extractor.py    # PDF + OCR (Tesseract, spa)
│   ├── word_extractor.py
│   ├── text_cleaner.py
│   ├── rule_engine.py
│   ├── ai_analyzer.py      # IA opcional
│   ├── scoring.py
│   └── evidence.py
├── rules/
│   └── checklist.yaml      # los 25 criterios
├── reports/
│   ├── excel_report.py
│   └── pdf_report.py
├── tests/
└── data/
    ├── tessdata/           # modelos de idioma para OCR
    └── temp/
```

## Pruebas

```bash
.venv\Scripts\python -m pytest
```

## Nota de alcance

El OCR reconoce texto, pero **no valida firmas ni la validez jurídica** de las cláusulas. Los resultados son una ayuda de revisión y no sustituyen el criterio de un asesor.
