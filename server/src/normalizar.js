import natural from 'natural'
import levenshtein from 'js-levenshtein'

// ── Normalización de texto ─────────────────────────────────────────────────
export function normalizarTexto(s) {
  return (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
}

export function tokenizar(s) {
  return normalizarTexto(s).split(/[^a-z0-9ñ%]+/).filter(Boolean)
}

export function stem(palabra) {
  const p = normalizarTexto(palabra)
  try {
    return natural.PorterStemmerEs.stem(p)
  } catch {
    return p
  }
}

// ── Números en letras → dígitos ────────────────────────────────────────────
const NUMEROS = {
  uno: 1, una: 1, dos: 2, tres: 3, cuatro: 4, cinco: 5, seis: 6, siete: 7,
  ocho: 8, nueve: 9, diez: 10, once: 11, doce: 12, trece: 13, catorce: 14,
  quince: 15, dieciseis: 16, diecisiete: 17, dieciocho: 18, diecinueve: 19,
  veinte: 20, treinta: 30, cuarenta: 40, cincuenta: 50, sesenta: 60,
  setenta: 70, ochenta: 80, noventa: 90, cien: 100, ciento: 100
}

const NUM_WORD = Object.keys(NUMEROS).join('|')
const UNIDAD_NORM = { dia: 'dias', días: 'dias', dias: 'dias', mes: 'meses', meses: 'meses', año: 'años', anos: 'años', anio: 'años', anios: 'años', años: 'años' }

export function normalizarUnidad(u) {
  return UNIDAD_NORM[normalizarTexto(u)] || normalizarTexto(u)
}

// ── Extracción de porcentajes y plazos ─────────────────────────────────────
export function extraerPorcentajes(texto) {
  const t = normalizarTexto(texto)
  const encontrados = []
  const reDigit = /(\d+(?:[.,]\d+)?)\s*%/g
  let m
  while ((m = reDigit.exec(t)) !== null) {
    encontrados.push(parseFloat(m[1].replace(',', '.')))
  }
  const reWord = new RegExp(`(${NUM_WORD})\\s+por\\s+ciento`, 'g')
  while ((m = reWord.exec(t)) !== null) {
    encontrados.push(NUMEROS[m[1]])
  }
  return encontrados
}

export function extraerPlazos(texto) {
  const t = normalizarTexto(texto)
  const encontrados = []
  const unidad = '(dias|día|meses|mes|años|anos|anios|año|anio)'
  const reDigit = new RegExp(`(\\d+)\\s*${unidad}`, 'g')
  let m
  while ((m = reDigit.exec(t)) !== null) {
    encontrados.push({ valor: parseInt(m[1], 10), unidad: normalizarUnidad(m[2]) })
  }
  const reWord = new RegExp(`(${NUM_WORD})\\s*(?:\\(\\s*\\d+\\s*\\)\\s*)?${unidad}`, 'g')
  while ((m = reWord.exec(t)) !== null) {
    encontrados.push({ valor: NUMEROS[m[1]], unidad: normalizarUnidad(m[2]) })
  }
  return encontrados
}

// ── Coincidencia de términos ───────────────────────────────────────────────
export function contieneTermino(textoNorm, termino) {
  return textoNorm.includes(normalizarTexto(termino))
}

export function coincideFuzzy(textoNorm, termino) {
  const tn = normalizarTexto(termino)
  if (tn.length < 5) return false
  const palabras = tokenizar(textoNorm)
  for (const p of palabras) {
    if (Math.abs(p.length - tn.length) > 2) continue
    const dist = levenshtein(p, tn)
    if (dist <= 1 || dist / Math.max(tn.length, 1) <= 0.2) return true
  }
  return false
}

// ── Negación ───────────────────────────────────────────────────────────────
const NEGACIONES = ['no', 'sin', 'exento', 'exenta', 'excluido', 'excluida', 'unilateral', 'excepto', 'salvo', 'no aplica']

export function tieneNegacionCerca(textoNorm, termino, radio = 6) {
  const idx = textoNorm.indexOf(normalizarTexto(termino))
  if (idx === -1) return false
  const tokens = textoNorm.split(/\s+/)
  const antes = textoNorm.slice(Math.max(0, idx - 80), idx).split(/\s+/).slice(-radio)
  const despues = textoNorm.slice(idx, idx + 80).split(/\s+/).slice(0, radio)
  const ventana = [...antes, ...despues].join(' ')
  return NEGACIONES.some((n) => ventana.includes(n))
}
