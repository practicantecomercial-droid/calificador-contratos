import { useEffect, useState } from 'react'
import { api } from '../api.js'

const hoy = () => new Date().toISOString().slice(0, 10)

export default function EvaluarPage({ id, nav }) {
  const [criterios, setCriterios] = useState([])
  const [nombre, setNombre] = useState('')
  const [fecha, setFecha] = useState(hoy())
  const [obsGeneral, setObsGeneral] = useState('')
  const [items, setItems] = useState({})
  const [guardado, setGuardado] = useState(null)
  const [error, setError] = useState('')

  const [documento, setDocumento] = useState(null)
  const [extrayendo, setExtrayendo] = useState(false)
  const [analizando, setAnalizando] = useState(false)
  const [iaDisponible, setIaDisponible] = useState(true)
  const [iaError, setIaError] = useState('')
  const [mostrarTexto, setMostrarTexto] = useState(false)

  const esEdicion = Boolean(id)

  useEffect(() => {
    async function init() {
      const criterios = await api.listarCriterios()
      setCriterios(criterios)

      api.iaDisponible().then((r) => setIaDisponible(r.disponible)).catch(() => {})

      if (esEdicion) {
        const ev = await api.obtenerEvaluacion(id)
        setNombre(ev.nombre_contrato)
        setFecha(ev.fecha)
        setObsGeneral(ev.observacion_general || '')
        const mapa = {}
        for (const it of ev.items) {
          mapa[it.criterio_id] = { cumple: it.cumple, observacion: it.observacion || '' }
        }
        setItems(mapa)
      } else {
        const mapa = {}
        for (const c of criterios) {
          mapa[c.id] = { cumple: false, observacion: '' }
        }
        setItems(mapa)
      }
    }
    init()
  }, [id])

  function setCumple(criterioId, cumple) {
    setItems((prev) => ({ ...prev, [criterioId]: { ...prev[criterioId], cumple } }))
  }

  function setObs(criterioId, observacion) {
    setItems((prev) => ({ ...prev, [criterioId]: { ...prev[criterioId], observacion } }))
  }

  const total = criterios.length
  const cumplidos = criterios.filter((c) => items[c.id]?.cumple).length
  const porcentaje = total === 0 ? 0 : Math.round((cumplidos / total) * 100)

  async function alSubirArchivo(e) {
    const file = e.target.files[0]
    if (!file) return
    setError('')
    setIaError('')
    setExtrayendo(true)
    try {
      const res = await api.extraerDocumento(file)
      setDocumento({ nombre: res.nombre, texto: res.texto })
    } catch (err) {
      setError(err.message)
    } finally {
      setExtrayendo(false)
      e.target.value = ''
    }
  }

  function aplicarResultados(resultados) {
    setItems((prev) => {
      const mapa = { ...prev }
      for (const r of resultados) {
        const cid = r.criterio_id
        const estado = r.estado || (r.cumple ? 'cumple' : 'no_cumple')
        mapa[cid] = {
          cumple: estado === 'cumple',
          estado,
          observacion: r.justificacion || ''
        }
      }
      return mapa
    })
  }

  async function analizar() {
    if (!documento) return
    setAnalizando(true)
    setIaError('')
    try {
      const { resultados } = await api.analizarConIA(documento.texto, criterios)
      aplicarResultados(resultados)
    } catch (err) {
      setIaError(err.message)
    } finally {
      setAnalizando(false)
    }
  }

  async function analizarLocalDoc() {
    if (!documento) return
    setAnalizando(true)
    setIaError('')
    try {
      const { resultados } = await api.analizarLocal(documento.texto, criterios)
      aplicarResultados(resultados)
    } catch (err) {
      setIaError(err.message)
    } finally {
      setAnalizando(false)
    }
  }

  async function guardar() {
    if (!nombre.trim()) {
      setError('Ingresa el nombre del contrato.')
      return
    }
    setError('')
    const payload = {
      nombre_contrato: nombre,
      fecha,
      observacion_general: obsGeneral,
      items: criterios.map((c) => ({
        criterio_id: c.id,
        criterio_texto: c.texto,
        cumple: items[c.id]?.cumple ?? false,
        observacion: items[c.id]?.observacion ?? ''
      }))
    }
    if (esEdicion) {
      await api.editarEvaluacion(id, payload)
      setGuardado(id)
    } else {
      const res = await api.crearEvaluacion(payload)
      setGuardado(res.id)
    }
  }

  return (
    <div className="page">
      <h2>{esEdicion ? 'Editar evaluación' : 'Evaluar contrato'}</h2>

      <div className="card form-grid">
        <label>
          Nombre del contrato
          <input type="text" value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Ej. Contrato con Acme S.A." />
        </label>
        <label>
          Fecha
          <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} />
        </label>
      </div>

      <div className="card">
        <h3>Cargar documento (opcional)</h3>
        <input type="file" accept=".pdf,.docx,.doc" onChange={alSubirArchivo} disabled={extrayendo} />
        {extrayendo && <p>Extrayendo texto…</p>}
        {documento && (
          <div className="doc-panel">
            <p className="doc-cargado">{documento.nombre} — {documento.texto.length} caracteres</p>
            <div className="doc-acciones">
              <button className="btn primary" onClick={analizar} disabled={analizando}>
                {analizando ? 'Analizando…' : 'Analizar con IA'}
              </button>
              <button className="btn" onClick={analizarLocalDoc} disabled={analizando}>
                Analizar local (sin IA)
              </button>
              <button className="btn" onClick={() => setMostrarTexto(!mostrarTexto)}>
                {mostrarTexto ? 'Ocultar texto' : 'Revisar manualmente (ver texto)'}
              </button>
            </div>
            {!iaDisponible && <p className="hint">Para usar la IA, agrega tu OPENAI_API_KEY en el archivo server\.env</p>}
            {iaError && <p className="error">{iaError}</p>}
            {mostrarTexto && (
              <details open>
                <summary>Texto extraído del documento</summary>
                <pre className="texto-doc">{documento.texto}</pre>
              </details>
            )}
          </div>
        )}
      </div>

      <div className="resumen">
        <strong>Puntaje:</strong> {cumplidos} de {total} cumplidos ({porcentaje}%)
      </div>

      {total === 0 && <p className="vacio">Agrega criterios primero en la pestaña «Criterios».</p>}

      <ul className="lista-evaluacion">
        {criterios.map((c, i) => {
          const estado = items[c.id]?.estado || (items[c.id]?.cumple ? 'cumple' : 'no_cumple')
          const etiquetas = { cumple: 'Cumple', parcial: 'Parcial', no_cumple: 'No cumple' }
          return (
          <li key={c.id} className={estado}>
            <div className="criterio-header">
              <span className="orden">{i + 1}.</span>
              <span className="texto">{c.texto}</span>
              {items[c.id]?.estado && <span className={`badge-estado badge-${estado}`}>{etiquetas[estado]}</span>}
            </div>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  name={`c-${c.id}`}
                  checked={items[c.id]?.cumple === true}
                  onChange={() => setCumple(c.id, true)}
                /> Sí
              </label>
              <label>
                <input
                  type="radio"
                  name={`c-${c.id}`}
                  checked={items[c.id]?.cumple === false}
                  onChange={() => setCumple(c.id, false)}
                /> No
              </label>
            </div>
            <input
              type="text"
              className="obs"
              placeholder="Observación (opcional)"
              value={items[c.id]?.observacion || ''}
              onChange={(e) => setObs(c.id, e.target.value)}
            />
          </li>
          )
        })}
      </ul>

      <div className="card">
        <label>
          Observación general
          <textarea value={obsGeneral} onChange={(e) => setObsGeneral(e.target.value)} rows={3} placeholder="Comentarios generales sobre el contrato…" />
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="acciones-footer">
        <button className="btn primary" onClick={guardar} disabled={total === 0}>Guardar evaluación</button>
        {guardado && (
          <>
            <button className="btn" onClick={() => nav.reporte(guardado)}>Ver reporte</button>
            <span className="ok">Guardado ✓</span>
          </>
        )}
      </div>
    </div>
  )
}
