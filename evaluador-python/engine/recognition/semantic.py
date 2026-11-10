"""Capa semántica offline (BM25) con reordenamiento opcional por LLM."""
from __future__ import annotations

import json
import math
import os
from collections import Counter

from .text import tokens

_K1 = 1.5
_B = 0.75
_ESCALA = 3.0


class IndiceBM25:
    """Índice BM25 puro en Python sobre las unidades del documento."""

    def __init__(self, textos, k1=_K1, b=_B):
        self.k1 = k1
        self.b = b
        self.documentos = [tokens(texto) for texto in textos]
        self.largos = [len(documento) for documento in self.documentos]
        self.total = len(self.documentos)
        self.largo_promedio = (
            sum(self.largos) / self.total if self.total else 1.0
        ) or 1.0
        self.frecuencias = [Counter(documento) for documento in self.documentos]
        self.frecuencia_documental = Counter()
        for documento in self.documentos:
            self.frecuencia_documental.update(set(documento))
        self.idf = {
            termino: math.log(
                1 + (self.total - frecuencia + 0.5) / (frecuencia + 0.5)
            )
            for termino, frecuencia in self.frecuencia_documental.items()
        }

    def puntuar(self, consulta) -> list[float]:
        terminos = set(tokens(consulta))
        puntajes = []
        for i, frecuencias in enumerate(self.frecuencias):
            largo = self.largos[i]
            puntaje = 0.0
            for termino in terminos:
                frecuencia = frecuencias.get(termino, 0)
                if not frecuencia:
                    continue
                idf = self.idf.get(termino, 0.0)
                denominador = frecuencia + self.k1 * (
                    1 - self.b + self.b * largo / self.largo_promedio
                )
                puntaje += idf * frecuencia * (self.k1 + 1) / denominador
            puntajes.append(puntaje)
        return puntajes

    @staticmethod
    def normalizar_score(puntaje: float) -> float:
        if puntaje <= 0:
            return 0.0
        return round(puntaje / (puntaje + _ESCALA), 3)

    def mejores(self, consulta, top_k=3, umbral=0.15) -> list[tuple[int, float]]:
        """Devuelve ``(indice_unidad, score_normalizado)`` de los mejores."""
        pares = [
            (i, self.normalizar_score(puntaje))
            for i, puntaje in enumerate(self.puntuar(consulta))
            if puntaje > 0
        ]
        pares.sort(key=lambda par: par[1], reverse=True)
        return [(i, score) for i, score in pares[:top_k] if score >= umbral]


def reordenar_con_llm(consulta, candidatos, modelo=None):
    """Hook opcional: sin ``OPENAI_API_KEY`` devuelve los candidatos intactos.

    El LLM solo reordena candidatos ya recuperados; nunca decide el estado.
    Ante cualquier error se conserva el orden offline (fail-open).
    """
    if not candidatos or not os.getenv("OPENAI_API_KEY"):
        return candidatos
    try:
        from openai import OpenAI

        cliente = OpenAI()
        extracto = [
            {"indice": i, "texto": candidato.get("texto", "")[:600]}
            for i, candidato in enumerate(candidatos[:10])
        ]
        mensaje = (
            "Ordena los fragmentos por relevancia para la consulta. "
            "Responde solo con un arreglo JSON de índices, sin texto adicional.\n"
            f"Consulta: {consulta}\n"
            f"Fragmentos: {json.dumps(extracto, ensure_ascii=False)}"
        )
        respuesta = cliente.chat.completions.create(
            model=modelo or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": mensaje}],
            temperature=0,
        )
        orden = json.loads(respuesta.choices[0].message.content)
        indices = [
            indice for indice in orden
            if isinstance(indice, int) and 0 <= indice < len(candidatos)
        ]
        if not indices:
            return candidatos
        vistos = set(indices)
        reordenados = [candidatos[indice] for indice in indices]
        reordenados.extend(
            candidato for i, candidato in enumerate(candidatos) if i not in vistos
        )
        return reordenados
    except Exception:
        return candidatos
