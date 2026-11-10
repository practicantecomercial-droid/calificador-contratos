"""Regla determinista para GC-09 (pólizas y garantías)."""
from __future__ import annotations

from ..schema import (
    ESTADO_CUMPLE,
    ESTADO_NO_APLICA,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
)
from .common import (
    candidatos_con,
    finalizar,
    fragmentos_con,
    resultado,
    vigencia_meses,
)
from .generic import combinar_estado
from .operators import contiene_frase, porcentajes

_TERMINOS_POLIZA = ("poliza", "garantia", "amparo", "seguro")
_AMPAROS = {
    "cumplimiento": ("cumplimiento",),
    "buen_manejo": ("buen manejo", "manejo del anticipo", "manejo de anticipo"),
    "salarios": ("salarios", "prestaciones sociales", "obligaciones laborales"),
    "calidad": ("calidad",),
    "responsabilidad_civil": ("responsabilidad civil",),
}
_TERMINOS_AMPARO = tuple(
    termino for terminos in _AMPAROS.values() for termino in terminos
)
_EXCEPCION = ("excepcion", "excepciones")
_APROBACION = (
    "aprobad",
    "autorizad",
    "jefe administrativo",
    "director comercial",
)


def _vigencia_para(texto, terminos, meses_minimo):
    fragmentos = fragmentos_con(texto, terminos)
    if not fragmentos and contiene_frase(texto, terminos):
        fragmentos = [texto]
    for fragmento in fragmentos:
        meses = vigencia_meses(fragmento)
        if meses is not None:
            return meses >= meses_minimo, meses
    return None, None


def _amparos_presentes(texto):
    return [
        nombre
        for nombre, terminos in _AMPAROS.items()
        if contiene_frase(texto, terminos)
    ]


def _porcentajes_polizas(texto):
    valores = []
    for fragmento in fragmentos_con(texto, _TERMINOS_AMPARO):
        encontrados = porcentajes(fragmento)
        if encontrados:
            valores.append(encontrados[0])
    return valores


def _excepcion_aprobada(texto):
    return contiene_frase(texto, _EXCEPCION) and contiene_frase(texto, _APROBACION)


def _validar_identificacion(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _TERMINOS_POLIZA):
        return resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificaron pólizas ni garantías en el contrato.",
        )
    return resultado(
        subrequisito,
        ESTADO_CUMPLE,
        candidatos_con(candidatos, _TERMINOS_POLIZA),
        "El contrato identifica pólizas o garantías exigidas.",
    )


def _validar_amparos(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _TERMINOS_POLIZA):
        return resultado(
            subrequisito,
            ESTADO_NO_IDENTIFICADO,
            [],
            "No se identificaron pólizas ni garantías.",
        )
    presentes = _amparos_presentes(texto)
    evidencia = candidatos_con(candidatos, _TERMINOS_AMPARO)
    if presentes:
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            evidencia,
            "Amparos identificados: " + ", ".join(presentes) + ".",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        evidencia,
        "Se mencionan pólizas pero no se enumeran amparos concretos.",
    )


def _validar_vigencia(subrequisito, candidatos, texto, nombre, meses_minimo):
    terminos = _AMPAROS[nombre]
    if not contiene_frase(texto, terminos):
        return resultado(
            subrequisito,
            ESTADO_NO_APLICA,
            [],
            f"El contrato no exige amparo de {nombre.replace('_', ' ')}.",
        )

    evidencia = candidatos_con(candidatos, terminos)
    cumple, meses = _vigencia_para(texto, terminos, meses_minimo)
    if cumple is True:
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            evidencia,
            f"Vigencia de {meses} meses cumple el mínimo de {meses_minimo}.",
        )
    if cumple is False:
        if _excepcion_aprobada(texto):
            return resultado(
                subrequisito,
                ESTADO_REVISION_HUMANA,
                evidencia,
                f"Vigencia de {meses} meses; existe una excepción que requiere validación.",
            )
        return resultado(
            subrequisito,
            ESTADO_NO_CUMPLE,
            evidencia,
            f"Vigencia de {meses} meses es inferior al mínimo de {meses_minimo}.",
        )
    return resultado(
        subrequisito,
        ESTADO_PARCIAL,
        evidencia,
        "Se exige el amparo pero no se establece su vigencia.",
    )


def _validar_suma(subrequisito, candidatos, texto):
    valores = _porcentajes_polizas(texto)
    evidencia = candidatos_con(candidatos, _TERMINOS_AMPARO)
    if len(valores) >= 2:
        total = sum(valores)
        if total <= 100:
            return resultado(
                subrequisito,
                ESTADO_CUMPLE,
                evidencia,
                f"La suma de pólizas ({total:g}%) no supera el 100%.",
            )
        return resultado(
            subrequisito,
            ESTADO_NO_CUMPLE,
            evidencia,
            f"La suma de pólizas ({total:g}%) supera el 100%.",
        )
    if len(valores) == 1:
        return resultado(
            subrequisito,
            ESTADO_PARCIAL,
            evidencia,
            f"Solo se identificó un porcentaje de póliza ({valores[0]:g}%).",
        )
    return resultado(
        subrequisito,
        ESTADO_NO_IDENTIFICADO,
        evidencia,
        "No se identificaron porcentajes de pólizas comparables.",
    )


def _validar_excepciones(subrequisito, candidatos, texto):
    if not contiene_frase(texto, _EXCEPCION):
        return resultado(
            subrequisito,
            ESTADO_NO_APLICA,
            [],
            "No se registran excepciones a las pólizas.",
        )
    evidencia = candidatos_con(candidatos, _EXCEPCION)
    if contiene_frase(texto, _APROBACION):
        return resultado(
            subrequisito,
            ESTADO_CUMPLE,
            evidencia,
            "La excepción cuenta con evidencia de validación.",
        )
    return resultado(
        subrequisito,
        ESTADO_REVISION_HUMANA,
        evidencia,
        "Hay una excepción sin evidencia de validación.",
    )


def _observacion_gc09(estado, resultados):
    if estado == ESTADO_CUMPLE:
        return "Pólizas identificadas y verificadas."
    if estado == ESTADO_NO_CUMPLE:
        incumplidos = [
            item["subrequisito_id"]
            for item in resultados
            if item["estado"] == ESTADO_NO_CUMPLE
        ]
        return "Pólizas no conformes: " + ", ".join(incumplidos) + "."
    if estado == ESTADO_PARCIAL:
        pendientes = [
            item["subrequisito_id"]
            for item in resultados
            if item["estado"] in (ESTADO_NO_IDENTIFICADO, ESTADO_PARCIAL)
        ]
        return "Verificación de pólizas incompleta: " + ", ".join(pendientes) + "."
    if estado == ESTADO_REVISION_HUMANA:
        return "Pólizas con excepciones o vigencias que requieren revisión humana."
    if estado == ESTADO_NO_APLICA:
        return "No aplica para este contrato."
    return "No se identificaron pólizas ni garantías exigidas."


def validar_gc09(criterio, reconocimiento, contexto=None, texto_documento=""):
    """Valida la identificación, vigencias y suma de pólizas."""
    texto = texto_documento or (contexto or {}).get("observaciones", "")
    candidatos = reconocimiento.get("subrequisitos", {})
    subrequisitos = {
        subrequisito["id"]: subrequisito
        for subrequisito in criterio.get("subrequisitos", [])
    }

    validadores = {
        "GC-09.1": lambda sub: _validar_identificacion(
            sub, candidatos.get("GC-09.1", []), texto
        ),
        "GC-09.2": lambda sub: _validar_amparos(
            sub, candidatos.get("GC-09.2", []), texto
        ),
        "GC-09.3": lambda sub: _validar_vigencia(
            sub, candidatos.get("GC-09.3", []), texto, "salarios", 36
        ),
        "GC-09.4": lambda sub: _validar_vigencia(
            sub, candidatos.get("GC-09.4", []), texto, "calidad", 12
        ),
        "GC-09.5": lambda sub: _validar_suma(
            sub, candidatos.get("GC-09.5", []), texto
        ),
        "GC-09.6": lambda sub: _validar_excepciones(
            sub, candidatos.get("GC-09.6", []), texto
        ),
    }

    resultados = [
        validadores[subrequisito_id](subrequisitos[subrequisito_id])
        for subrequisito_id in validadores
        if subrequisito_id in subrequisitos
    ]
    estado = combinar_estado(resultados)
    return finalizar(
        criterio,
        resultados,
        contexto,
        observacion=_observacion_gc09(estado, resultados),
    )
