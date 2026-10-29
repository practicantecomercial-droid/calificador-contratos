import {
  normalizarTexto, tokenizar, stem, contieneTermino, coincideFuzzy,
  extraerPorcentajes, extraerPlazos, normalizarUnidad
} from './normalizar.js'
import { CONFIG } from './criterios-config.js'

function terminoCoincide(textoNorm, termino) {
  const tn = normalizarTexto(termino)
  if (!tn) return false
  if (contieneTermino(textoNorm, tn)) return true
  if (tn.includes(' ')) return false
  const ts = stem(tn)
  for (const tok of tokenizar(textoNorm)) {
    if (stem(tok) === ts) return true
  }
  if (tn.length >= 5) return coincideFuzzy(textoNorm, tn)
  return false
}

function evaluarPatron(patron, texto) {
  if (!patron) return true
  if (patron.tipo === 'porcentaje') {
    const valores = extraerPorcentajes(texto)
    return valores.some((v) => Math.abs(v - patron.valor) < 0.5)
  }
  if (patron.tipo === 'plazo') {
    const plazos = extraerPlazos(texto)
    const unidad = normalizarUnidad(patron.unidad)
    const comparacion = patron.comparacion || '='
    return plazos.some((p) => {
      if (p.unidad !== unidad) return false
      if (comparacion === '>=') return p.valor >= patron.valor
      if (comparacion === '<=') return p.valor <= patron.valor
      return p.valor === patron.valor
    })
  }
  return false
}

function negadoPor(textoNorm, termino, negaciones) {
  const idx = textoNorm.indexOf(normalizarTexto(termino))
  if (idx === -1) return false
  const ventana = textoNorm.slice(Math.max(0, idx - 60), idx + 60)
  return negaciones.some((n) => ventana.includes(normalizarTexto(n)))
}

function configPorDefecto(criterio) {
  const palabras = tokenizar(criterio.texto).filter((p) => p.length >= 4)
  return {
    nombre: criterio.texto,
    minimo: 1,
    subItems: [{ nombre: 'Referencia', terminos: palabras.slice(0, 8) }]
  }
}

function evaluarCriterio(criterio, textoNorm, texto) {
  const cfg = CONFIG[criterio.id] || configPorDefecto(criterio)
  const encontrados = []
  const faltantes = []

  for (const sub of cfg.subItems) {
    const terminos = sub.terminos || []
    const terminosencontrados = terminos.filter((t) => terminoCoincide(textoNorm, t))
    const patronCumple = evaluarPatron(sub.patron, texto)
    const negado = sub.negacion && terminosencontrados.some((t) => negadoPor(textoNorm, t, sub.negacion))

    const cumple = (terminos.length === 0 || terminosencontrados.length > 0) && patronCumple && !negado
    if (cumple) encontrados.push(sub.nombre)
    else faltantes.push(sub.nombre)
  }

  const total = cfg.subItems.length
  const cumplidos = encontrados.length
  const minimo = Math.min(cfg.minimo || 1, total)

  let estado
  if (cumplidos >= minimo) estado = 'cumple'
  else if (cumplidos > 0) estado = 'parcial'
  else estado = 'no_cumple'

  let justificacion
  if (estado === 'cumple') {
    justificacion = `Cumple (${cumplidos}/${total}): ${encontrados.join(', ')}`
  } else if (estado === 'parcial') {
    justificacion = `Parcial (${cumplidos}/${total}). Encontrado: ${encontrados.join(', ') || '—'}. Falta: ${faltantes.join(', ')}`
  } else {
    justificacion = `No cumple. Falta: ${faltantes.join(', ')}`
  }

  return {
    criterio_id: criterio.id,
    cumple: estado === 'cumple',
    estado,
    cobertura: `${cumplidos}/${total}`,
    encontrados,
    faltantes,
    justificacion
  }
}

export function analizarLocal(texto, criterios) {
  const textoNorm = normalizarTexto(texto)
  return criterios.map((c) => evaluarCriterio(c, textoNorm, texto))
}
