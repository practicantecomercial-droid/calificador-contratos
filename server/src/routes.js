import { Router } from 'express'
import multer from 'multer'
import { readData, writeData, nextId } from './store.js'
import { extraerTexto } from './extract.js'
import { analizarConIA, apiKeyDisponible } from './ai.js'
import { analizarLocal } from './local.js'

const router = Router()
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 20 * 1024 * 1024 } })

// ── Documento e IA ─────────────────────────────────────────────────────────
router.post('/extraer', upload.single('documento'), async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'No se recibió archivo' })
    const texto = await extraerTexto(req.file.buffer, req.file.originalname)
    res.json({ nombre: req.file.originalname, texto })
  } catch (e) {
    res.status(400).json({ error: e.message })
  }
})

router.get('/ia/disponible', (req, res) => {
  res.json({ disponible: apiKeyDisponible() })
})

router.post('/analizar', async (req, res) => {
  try {
    const { texto, criterios } = req.body || {}
    if (!texto || !criterios || !Array.isArray(criterios)) {
      return res.status(400).json({ error: 'texto y criterios requeridos' })
    }
    const resultados = await analizarConIA(texto, criterios)
    res.json({ resultados })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

router.post('/analizar-local', (req, res) => {
  const { texto, criterios } = req.body || {}
  if (!texto || !criterios || !Array.isArray(criterios)) {
    return res.status(400).json({ error: 'texto y criterios requeridos' })
  }
  const resultados = analizarLocal(texto, criterios)
  res.json({ resultados })
})

// ── Criterios ──────────────────────────────────────────────────────────────
router.get('/criterios', (req, res) => {
  const data = readData()
  const criterios = data.criterios
    .filter((c) => c.activo !== false)
    .sort((a, b) => a.orden - b.orden || a.id - b.id)
  res.json(criterios)
})

router.post('/criterios', (req, res) => {
  const { texto } = req.body || {}
  if (!texto || !texto.trim()) return res.status(400).json({ error: 'texto requerido' })
  const data = readData()
  const orden = data.criterios.reduce((m, c) => Math.max(m, c.orden), -1) + 1
  const criterio = { id: nextId(data.criterios), texto: texto.trim(), activo: true, orden }
  data.criterios.push(criterio)
  writeData(data)
  res.status(201).json(criterio)
})

router.put('/criterios/:id', (req, res) => {
  const { texto } = req.body || {}
  if (!texto || !texto.trim()) return res.status(400).json({ error: 'texto requerido' })
  const data = readData()
  const criterio = data.criterios.find((c) => c.id === Number(req.params.id))
  if (!criterio) return res.status(404).json({ error: 'no encontrado' })
  criterio.texto = texto.trim()
  writeData(data)
  res.json(criterio)
})

router.put('/criterios/:id/orden', (req, res) => {
  const { orden } = req.body || {}
  if (typeof orden !== 'number') return res.status(400).json({ error: 'orden requerido' })
  const data = readData()
  const criterio = data.criterios.find((c) => c.id === Number(req.params.id))
  if (!criterio) return res.status(404).json({ error: 'no encontrado' })
  criterio.orden = orden
  writeData(data)
  res.json({ ok: true })
})

router.delete('/criterios/:id', (req, res) => {
  const data = readData()
  const criterio = data.criterios.find((c) => c.id === Number(req.params.id))
  if (!criterio) return res.status(404).json({ error: 'no encontrado' })
  criterio.activo = false
  writeData(data)
  res.json({ ok: true })
})

// ── Evaluaciones ───────────────────────────────────────────────────────────
router.get('/evaluaciones', (req, res) => {
  const data = readData()
  const evaluaciones = data.evaluaciones
    .map((e) => {
      const total = e.items.length
      const cumplidos = e.items.filter((i) => i.cumple).length
      return { id: e.id, nombre_contrato: e.nombre_contrato, fecha: e.fecha, total, cumplidos }
    })
    .sort((a, b) => b.id - a.id)
  res.json(evaluaciones)
})

router.get('/evaluaciones/:id', (req, res) => {
  const data = readData()
  const ev = data.evaluaciones.find((e) => e.id === Number(req.params.id))
  if (!ev) return res.status(404).json({ error: 'no encontrada' })
  res.json(ev)
})

router.post('/evaluaciones', (req, res) => {
  const { nombre_contrato, fecha, observacion_general = '', items = [] } = req.body || {}
  if (!nombre_contrato || !nombre_contrato.trim()) {
    return res.status(400).json({ error: 'nombre_contrato requerido' })
  }
  if (!Array.isArray(items)) return res.status(400).json({ error: 'items inválido' })

  const data = readData()
  const fechaFinal = fecha || new Date().toISOString().slice(0, 10)
  const evaluacion = {
    id: nextId(data.evaluaciones),
    nombre_contrato: nombre_contrato.trim(),
    fecha: fechaFinal,
    observacion_general,
    items: items.map((it) => ({
      criterio_id: it.criterio_id ?? null,
      criterio_texto: it.criterio_texto ?? '',
      cumple: it.cumple ? true : false,
      observacion: it.observacion ?? ''
    }))
  }
  data.evaluaciones.push(evaluacion)
  writeData(data)
  res.status(201).json({ id: evaluacion.id })
})

router.put('/evaluaciones/:id', (req, res) => {
  const { nombre_contrato, fecha, observacion_general = '', items = [] } = req.body || {}
  const data = readData()
  const ev = data.evaluaciones.find((e) => e.id === Number(req.params.id))
  if (!ev) return res.status(404).json({ error: 'no encontrada' })
  if (!nombre_contrato || !nombre_contrato.trim()) {
    return res.status(400).json({ error: 'nombre_contrato requerido' })
  }
  ev.nombre_contrato = nombre_contrato.trim()
  ev.fecha = fecha
  ev.observacion_general = observacion_general
  ev.items = items.map((it) => ({
    criterio_id: it.criterio_id ?? null,
    criterio_texto: it.criterio_texto ?? '',
    cumple: it.cumple ? true : false,
    observacion: it.observacion ?? ''
  }))
  writeData(data)
  res.json({ ok: true })
})

router.delete('/evaluaciones/:id', (req, res) => {
  const data = readData()
  data.evaluaciones = data.evaluaciones.filter((e) => e.id !== Number(req.params.id))
  writeData(data)
  res.json({ ok: true })
})

export default router
