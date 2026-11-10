"""Evaluación del expediente y de la evidencia externa al contrato.

El contrato solo prueba lo que está escrito. Varios criterios describen
actividades administrativas que se confirman con otros archivos (pólizas,
cotizaciones firmadas, comprobantes, bitácora, etc.). Este módulo lee esos
archivos, busca la evidencia y produce un resultado con alcance EXPEDIENTE.
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

from .document_reader import leer_documento
from .knowledge_base import cargar_base_conocimiento
from .schema import (
    ALCANCE_EXPEDIENTE,
    ALCANCE_EVIDENCIA_EXTERNA,
    ESTADO_CUMPLE,
    ESTADO_NO_CUMPLE,
    ESTADO_NO_IDENTIFICADO,
    ESTADO_PARCIAL,
    ESTADO_REVISION_HUMANA,
    ESTADOS,
    nuevo_resultado,
)
from .validation.operators import contiene_frase

EXTENSIONES = {
    ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp",
}

EVIDENCIAS = {
    "GC-01": (
        ("contrato fisico", "contrato firmado", "contrato original"),
        ("cotizacion",),
        ("costeo", "costos"),
        ("manual",),
        ("documentos sst", "seguridad y salud en el trabajo"),
        ("anexo",),
    ),
    "GC-07": (
        ("contrato",),
        ("cotizacion",),
        ("poliza", "garantia"),
        ("cuenta de cobro",),
    ),
    "GC-11": (
        ("contrato",),
        ("lista de documentos", "documentos de liquidacion"),
        ("soportes de cierre", "soporte de cierre", "acta de liquidacion"),
    ),
    "GC-15": (
        (
            "firma del director comercial",
            "firmado por el director comercial",
            "director comercial",
        ),
        (
            "firma de gerencia",
            "firmado por gerencia",
            "gerencia general",
            "gerente general",
        ),
    ),
    "GC-16": (
        ("dos copias", "dos ejemplares", "dos tantos"),
        ("cotizacion firmada", "cotizaciones firmadas"),
        (
            "firma previa del director comercial",
            "firma del director comercial",
            "firmado por el director comercial",
        ),
    ),
    "GC-17": (
        ("bitacora", "carpeta bitacora"),
        ("archivo escaneado", "archivos escaneados", "documento escaneado"),
        ("nombre de archivo", "nombres de archivo"),
    ),
    "GC-18": (
        ("relacion de contratos",),
        ("fecha de actualizacion", "actualizado", "actualizada"),
        ("firma", "firmado"),
    ),
    "GC-19": (
        ("correo enviado", "correo electronico", "email"),
        ("cuenta de cobro",),
        ("poliza", "garantia"),
        ("bitacora", "carpeta bitacora"),
    ),
    "GC-20": (
        ("poliza firmada", "polizas firmadas"),
        ("bitacora", "carpeta bitacora"),
    ),
    "GC-21": (
        ("correo al asesor", "correo enviado al asesor", "email al asesor"),
        ("soportes adjuntos", "documentos adjuntos", "anexos"),
        ("constancia de entrega fisica", "constancia de entrega"),
    ),
    "GC-22": (
        ("control entrega documentos", "formato control entrega documentos"),
        ("firmado", "firma"),
    ),
    "GC-23": (
        ("contrato firmado por la obra", "contrato firmado por el cliente"),
        ("constancia de entrega a administracion", "entrega a administracion"),
    ),
    "GC-24": (
        (
            "comprobante de pago",
            "confirmacion del abono",
            "abono recibido",
            "pago del anticipo",
        ),
        ("estado del pedido", "pedido generado", "orden generada"),
    ),
    "GC-25": (
        ("anexo de garantia", "anexo garantia"),
    ),
}


def resolver_archivos(archivos):
    """Convierte una ruta, carpeta o lista en archivos compatibles únicos."""
    if isinstance(archivos, (str, Path)):
        entradas = [archivos]
    else:
        entradas = list(archivos)

    encontrados = []
    for entrada in entradas:
        ruta = Path(entrada)
        if ruta.is_dir():
            encontrados.extend(
                sorted(
                    archivo
                    for archivo in ruta.rglob("*")
                    if archivo.is_file() and archivo.suffix.lower() in EXTENSIONES
                )
            )
        elif ruta.is_file():
            encontrados.append(ruta)
        else:
            raise FileNotFoundError(f"No existe el archivo: {ruta}")

    vistos = set()
    unicos = []
    for archivo in encontrados:
        clave = str(archivo.resolve())
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(archivo)
    return unicos


def leer_expediente(archivos):
    """Lee los archivos del expediente y registra los que no se puedan abrir."""
    rutas = resolver_archivos(archivos)
    documentos = []
    resumen = []
    errores = []

    if not rutas:
        errores.append({
            "archivo": str(archivos),
            "error": "El expediente no contiene archivos compatibles.",
        })

    for ruta in rutas:
        try:
            documento = leer_documento(ruta)
        except Exception as error:  # un archivo ilegible no invalida el resto
            errores.append({"archivo": str(ruta), "error": str(error)})
            resumen.append({
                "ruta": str(ruta),
                "nombre": ruta.name,
                "error": str(error),
            })
            continue

        texto = documento.get("texto", "")
        documentos.append({
            "ruta": str(ruta),
            "nombre": ruta.name,
            "texto": texto,
        })
        resumen.append({
            "ruta": str(ruta),
            "nombre": ruta.name,
            "formato": documento.get("formato"),
            "caracteres": len(texto),
            "paginas": len(documento.get("paginas", [])),
            "ocr": any(
                pagina.get("ocr")
                for pagina in documento.get("paginas", [])
            ),
        })

    return {
        "rutas": [str(ruta) for ruta in rutas],
        "archivos": resumen,
        "documentos": documentos,
        "errores": errores,
    }


def _grupos_para(criterio):
    criterio_id = criterio["criterio_id"]
    if criterio_id in EVIDENCIAS:
        return EVIDENCIAS[criterio_id]

    grupos = []
    for item in criterio.get("evidencia_externa", []):
        for parte in re.split(r",|\s+y\s+", item):
            parte = parte.strip(" .")
            if parte:
                grupos.append((parte,))
    return tuple(grupos)


def _buscar_grupo(grupo, documentos):
    for documento in documentos:
        texto = documento["nombre"] + "\n" + documento["texto"]
        for termino in grupo:
            if contiene_frase(texto, (termino,)):
                return {
                    "grupo": grupo[0],
                    "termino": termino,
                    "archivo": documento["nombre"],
                }
    return None


def _resultado_externo(criterio, documentos, grupos):
    encontrados = []
    faltantes = []
    for grupo in grupos:
        coincidencia = _buscar_grupo(grupo, documentos)
        if coincidencia:
            encontrados.append(coincidencia)
        else:
            faltantes.append("Evidencia externa: " + grupo[0])

    total = len(grupos)
    proporcion = len(encontrados) / total if total else 0.0
    if proporcion >= 0.75:
        estado = ESTADO_CUMPLE
    elif encontrados:
        estado = ESTADO_PARCIAL
    else:
        estado = ESTADO_NO_IDENTIFICADO

    if estado == ESTADO_CUMPLE:
        observacion = (
            f"Evidencia externa completa ({len(encontrados)}/{total})."
        )
    elif estado == ESTADO_PARCIAL:
        observacion = (
            f"Evidencia externa parcial ({len(encontrados)}/{total})."
        )
    else:
        observacion = "No se encontró evidencia externa en el expediente."

    return nuevo_resultado(
        criterio_id=criterio["criterio_id"],
        criterio=criterio["nombre"],
        numero=criterio["numero"],
        estado=estado,
        confianza=round(proporcion, 2),
        evidencia=encontrados,
        alcance=ALCANCE_EXPEDIENTE,
        informacion_faltante=faltantes,
        observacion=observacion,
        requiere_revision_humana=estado != ESTADO_CUMPLE,
    )


def _resumen(resultados):
    conteo = {estado: 0 for estado in ESTADOS}
    for resultado in resultados.values():
        conteo[resultado["estado"]] += 1
    return {
        "total_criterios": len(resultados),
        "conteo_estados": conteo,
        "requieren_revision": sum(
            1
            for resultado in resultados.values()
            if resultado["requiere_revision_humana"]
        ),
    }


def evaluar_expediente(archivos, *, base=None, criterios=None):
    """Evalúa la evidencia externa de los criterios que la requieren."""
    base = base if base is not None else cargar_base_conocimiento()
    seleccionados = set(criterios) if criterios is not None else None

    externos = [
        criterio
        for criterio in base.get("criterios", [])
        if criterio.get("requiere_evidencia_externa")
        and (seleccionados is None or criterio["criterio_id"] in seleccionados)
    ]

    expediente = leer_expediente(archivos)
    resultados = {}
    for criterio in externos:
        resultados[criterio["criterio_id"]] = _resultado_externo(
            criterio,
            expediente["documentos"],
            _grupos_para(criterio),
        )

    return {
        "archivos": expediente["archivos"],
        "errores": expediente["errores"],
        "criterios": list(resultados.values()),
        "resultados": resultados,
        "resumen": _resumen(resultados),
    }


def _unir(primera, segunda):
    salida = list(primera)
    for item in segunda:
        if item not in salida:
            salida.append(item)
    return salida


def _combinar_criterio(documental, expediente):
    final = copy.deepcopy(documental)
    final["resultado_documental"] = copy.deepcopy(documental)
    final["resultado_expediente"] = copy.deepcopy(expediente)

    estado_documental = documental["estado"]
    estado_expediente = expediente["estado"]
    final["evidencia"] = _unir(
        documental["evidencia"], expediente["evidencia"]
    )

    if estado_documental == ESTADO_NO_CUMPLE:
        if estado_expediente == ESTADO_CUMPLE:
            final["estado"] = ESTADO_REVISION_HUMANA
            final["confianza"] = max(
                documental["confianza"], expediente["confianza"]
            )
            final["alcance"] = ALCANCE_EXPEDIENTE
            final["requiere_revision_humana"] = True
            final["observacion"] = (
                "El contrato no cumple, pero el expediente aporta evidencia "
                "en contrario; requiere revisión humana."
            )
        return final

    if estado_expediente == ESTADO_CUMPLE:
        if estado_documental != ESTADO_CUMPLE:
            final["estado"] = ESTADO_CUMPLE
            final["confianza"] = max(
                documental["confianza"], expediente["confianza"]
            )
            final["alcance"] = ALCANCE_EXPEDIENTE
            final["requiere_revision_humana"] = False
            final["observacion"] = (
                "Confirmado con evidencia del expediente."
            )
        final["informacion_faltante"] = []
        return final

    if estado_expediente == ESTADO_PARCIAL:
        if estado_documental == ESTADO_CUMPLE:
            return final
        final["estado"] = ESTADO_PARCIAL
        final["confianza"] = max(
            documental["confianza"], expediente["confianza"]
        )
        final["alcance"] = ALCANCE_EXPEDIENTE
        final["requiere_revision_humana"] = True
        final["informacion_faltante"] = _unir(
            documental["informacion_faltante"],
            expediente["informacion_faltante"],
        )
        final["observacion"] = "Evidencia parcial en el expediente."
        return final

    if estado_documental != ESTADO_CUMPLE:
        final["alcance"] = ALCANCE_EVIDENCIA_EXTERNA
        final["requiere_revision_humana"] = True
        final["informacion_faltante"] = _unir(
            documental["informacion_faltante"],
            expediente["informacion_faltante"],
        )
    return final


def combinar_resultados(documental, expediente):
    """Combina los resultados documentales con los del expediente."""
    combinados = {}
    for criterio_id, resultado in documental.items():
        externo = expediente.get(criterio_id)
        if externo is None:
            combinados[criterio_id] = copy.deepcopy(resultado)
        else:
            combinados[criterio_id] = _combinar_criterio(resultado, externo)
    return combinados
