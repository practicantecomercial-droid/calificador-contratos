"""Análisis opcional con IA (OpenAI), en el mismo formato que el motor de reglas."""
import json
import os

import requests

API_URL = "https://api.openai.com/v1/chat/completions"


def api_key_disponible():
    return bool(os.getenv("OPENAI_API_KEY"))


def analyze_with_ai(texto, criterios, api_key=None):
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError(
            "Falta OPENAI_API_KEY. Configúrala en la variable de entorno o en un archivo .env"
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    lista = "\n".join(f'{c["id"]}. {c["nombre"]}' for c in criterios)

    max_chars = 120000
    recortado = texto if len(texto) <= max_chars else texto[:max_chars] + "\n…[documento recortado]"

    sistema = (
        "Eres un analista experto en contratos de obra y carpintería. Evalúa un documento "
        "de contrato contra una lista de criterios de gestión. Para cada criterio indica si "
        "se CUMPLE (true) o NO (false) según lo escrito en el documento, y da una justificación "
        "breve (máx 20 palabras). Si no se puede verificar, responde false y justifica "
        '"No se evidencia en el documento". Responde SOLO con un JSON válido con la forma: '
        '{"resultados":[{"criterio_id":1,"cumple":true,"justificacion":"texto"}]}.'
    )
    usuario = f"Criterios a evaluar:\n{lista}\n\nDocumento del contrato:\n{recortado}"

    resp = requests.post(
        API_URL,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        json={
            "model": model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": usuario},
            ],
        },
        timeout=120,
    )

    if not resp.ok:
        raise RuntimeError(f"Error de OpenAI ({resp.status_code}): {resp.text[:300]}")

    contenido = resp.json()["choices"][0]["message"]["content"]
    parsed = json.loads(contenido)
    resultados = parsed.get("resultados", parsed)

    # Convertir al mismo formato que el motor de reglas.
    out = []
    for r in resultados:
        cumple = bool(r.get("cumple"))
        out.append({
            "criterio_id": r.get("criterio_id"),
            "nombre": r.get("nombre", ""),
            "estado": "cumple" if cumple else "no_cumple",
            "cumplidos": 1 if cumple else 0,
            "total": 1,
            "encontrados": [],
            "faltantes": [],
            "justificacion": r.get("justificacion", ""),
        })
    return out
