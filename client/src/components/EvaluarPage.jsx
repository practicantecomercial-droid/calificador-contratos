import { useEffect, useRef, useState } from 'react'
import { api } from '../api.js'

const hoy = () => new Date().toISOString().slice(0, 10)

const ESTADOS = {
  cumple: { label: 'Cumple', clase: 'cumple' },
  parcial: { label: 'Parcial', clase: 'parcial' },
  no_cumple: { label: 'No cumple', clase: 'no_cumple' },
  sin_evaluar: { label: 'Sin evaluar', clase: 'sin' }
}

const FILTROS = [
  { key: 'todos', label: 'Todos' },
  { key: 'cumple', label: 'Cumple' },
  { key: 'parcial', label: 'Parcial' },
  { key: 'no_cumple', label: 'No cumple' },
  { key: 'sin_evaluar', label: 'Sin evaluar' }
]

function IconUpload() {
  return (
    <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 16V4" /><path d="m7 9 5-5 5 5" /><path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
    </svg>
  )
}

function IconFile() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6" />
    </svg>
  )
}

export default function EvaluarPage({ id, nav }) {
  const [criterios, setCriterios] = useState([])
  const [nombre, setNombre] = useState('')
  const [fecha, setFecha] = useState(hoy())
  const [obsGeneral, setObsGeneral] = useState('')
  const [items, setItems] = useState({})
  const [guardado, setGuardado] = useState(null)
  const [error, setError] = useState('')
  const [filtro, setFiltro] = useState('todos')

  const [documento, setDocumento] = useState(null)
  const [extrayendo, setExtrayendo] = useState(false)
  const [analizando, setAnalizando] = useState(null)
  const [iaDisponible, setIaDisponible] = useState(true)
  const [iaError, setIaError] = useState('')
  const [mostrarTexto, setMostrarTexto] = useState(false)
  const [arrastrando, setArrastrando] = useState(false)
  const fileRef = useRef(null)

  const esEdicion = Boolean(id)

  useEffect(() => {
    async function init() {
      const lista = await api.listarCriterios()
      setCriterios(lista)

      api.iaDisponible().then((r) => setIaDisponible(r.disponible)).catch(() => {})

      if (esEdicion) {
        const ev = await api.obtenerEvaluacion(id)
        setNombre(ev.nombre_contrato)
        setFecha(ev.fecha)
        setObsGeneral(ev.observacion_general || '')
        const mapa = {}
        for (const it of ev.items) {
          mapa[it.criterio_id] = {
            estado: it.estado || (it.cumple ? 'cumple' : 'no_cumple'),
            confianza: it.confianza ?? null,
            observacion: it.observacion || ''
          }
        }
        setItems(mapa)
      } else {
        const mapa = {}
        for (const c of lista) mapa[c.id] = { estado: null, observacion: '' }
        setItems(mapa)
      }
    }
    init()
  }, [id])

  function setEstado(criterioId, estado) {
    setItems((prev) => ({ ...prev, [criterioId]: { ...prev[criterioId], estado } }))
    setGuardado(null)
  }

  function limpiarEstado(criterioId) {
    setItems((prev) => ({ ...prev, [criterioId]: { ...prev[criterioId], estado: null } }))
    setGuardado(null)
  }

  function setObs(criterioId, observacion) {
    setItems((prev) => ({ ...prev, [criterioId]: { ...prev[criterioId], observacion } }))
  }

  const total = criterios.length
  const counts = { cumple: 0, parcial: 0, no_cumple: 0, sin_evaluar: 0 }
  for (const c of criterios) {
    const est = items[c.id]?.estado
    if (est && counts[est] !== undefined) counts[est] += 1
    else counts.sin_evaluar += 1
  }
  const evaluados = counts.cumple + counts.parcial + counts.no_cumple
  const puntaje = total === 0 ? 0 : Math.round(((counts.cumple + 0.5 * counts.parcial) / total) * 100)

  const listaFiltrada = criterios.filter((c) => {
    if (filtro === 'todos') return true
    const est = items[c.id]?.estado || 'sin_evaluar'
    return est === filtro
  })

  function marcarTodoCumple() {
    const mapa = { ...items }
    for (const c of criterios) mapa[c.id] = { ...mapa[c.id], estado: 'cumple' }
    setItems(mapa)
    setGuardado(null)
  }

  function limpiarTodo() {
    const mapa = { ...items }
    for (const c of criterios) mapa[c.id] = { ...mapa[c.id], estado: null }
    setItems(mapa)
    setGuardado(null)
  }

  async function procesarArchivo(file) {
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
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  function onDrop(e) {
    e.preventDefault()
    setArrastrando(false)
    const file = e.dataTransfer.files?.[0]
    if (file) procesarArchivo(file)
  }

  function quitarDocumento() {
    setDocumento(null)
    setMostrarTexto(false)
    if (fileRef.current) fileRef.current.value = ''
  }

  function aplicarResultados(resultados) {
    setItems((prev) => {
      const mapa = { ...prev }
      for (const r of resultados) {
        const cid = r.criterio_id
        let estado = r.estado || (r.cumple ? 'cumple' : 'no_cumple')
        if (!ESTADOS[estado]) estado = 'parcial'
        mapa[cid] = {
          ...mapa[cid],
          estado,
          confianza: typeof r.confianza === 'number' ? r.confianza : null,
          cobertura: r.cobertura || null,
          encontrados: r.encontrados || null,
          faltantes: r.faltantes || null,
          observacion: r.justificacion || mapa[cid]?.observacion || ''
        }
      }
      return mapa
    })
    setGuardado(null)
  }

  async function analizarConIA() {
    if (!documento) return
    setAnalizando('ia')
    setIaError('')
    try {
      const { resultados } = await api.analizarConIA(documento.texto, criterios)
      aplicarResultados(resultados)
    } catch (err) {
      setIaError(err.message)
    } finally {
      setAnalizando(null)
    }
  }

  async function analizarLocal() {
    if (!documento) return
    setAnalizando('local')
    setIaError('')
    try {
      const { resultados } = await api.analizarLocal(documento.texto, criterios)
      aplicarResultados(resultados)
    } catch (err) {
      setIaError(err.message)
    } finally {
      setAnalizando(null)
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
      items: criterios.map((c) => {
        const it = items[c.id] || {}
        return {
          criterio_id: c.id,
          criterio_texto: c.texto,
          cumple: it.estado === 'cumple',
          estado: it.estado || 'sin_evaluar',
          confianza: it.confianza ?? null,
          observacion: it.observacion ?? ''
        }
      })
    }
    try {
      if (esEdicion) {
        await api.editarEvaluacion(id, payload)
        setGuardado(id)
      } else {
        const res = await api.crearEvaluacion(payload)
        setGuardado(res.id)
      }
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page page-evaluar">
      <div className="page-head">
        <div>
          <h2>{esEdicion ? 'Editar evaluación' : 'Evaluar contrato'}</h2>
          <p className="page-sub">Marca cada criterio como cumple, parcial o no cumple. El puntaje se calcula en tiempo real.</p>
        </div>
      </div>

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
        <div className="card-head">
          <h3 className="card-title">Documento del contrato</h3>
          <span className="tag">opcional</span>
        </div>

        <label
          className={`dropzone ${arrastrando ? 'is-drag' : ''} ${extrayendo ? 'is-busy' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setArrastrando(true) }}
          onDragLeave={() => setArrastrando(false)}
          onDrop={onDrop}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx,.doc"
            onChange={(e) => procesarArchivo(e.target.files?.[0])}
            disabled={extrayendo}
            hidden
          />
          <span className="dropzone-icon"><IconUpload /></span>
          {extrayendo ? (
            <span className="dropzone-text">Extrayendo texto…</span>
          ) : (
            <span className="dropzone-text"><strong>Arrastra</strong> tu PDF o DOCX aquí, o <strong>haz clic</strong> para seleccionar</span>
          )}
          <small className="dropzone-hint">PDF, DOCX o DOC · máximo 20 MB</small>
        </label>

        {documento && (
          <div className="doc-panel">
            <div className="doc-file">
              <span className="doc-file-icon"><IconFile /></span>
              <div className="doc-meta">
                <strong>{documento.nombre}</strong>
                <span>{documento.texto.length.toLocaleString('es-CO')} caracteres extraídos</span>
              </div>
              <button type="button" className="btn ghost sm" onClick={quitarDocumento}>Quitar</button>
            </div>
            <div className="doc-acciones">
              <button type="button" className="btn primary" onClick={analizarConIA} disabled={Boolean(analizando) || !iaDisponible}>
                {analizando === 'ia' ? 'Analizando…' : 'Analizar con IA'}
              </button>
              <button type="button" className="btn" onClick={analizarLocal} disabled={Boolean(analizando)}>
                {analizando === 'local' ? 'Analizando…' : 'Analizar local'}
              </button>
              <button type="button" className="btn ghost" onClick={() => setMostrarTexto((v) => !v)}>
                {mostrarTexto ? 'Ocultar texto' : 'Ver texto extraído'}
              </button>
            </div>
            {!iaDisponible && (
              <p className="hint">IA no configurada: agrega <code>OPENAI_API_KEY</code> en <code>server/.env</code>. Mientras tanto puedes usar el análisis local.</p>
            )}
            {iaError && <p className="error">{iaError}</p>}
            {mostrarTexto && <pre className="texto-doc">{documento.texto}</pre>}
          </div>
        )}
      </div>

      <div className="eval-toolbar">
        <div className="eval-score">
          <div className="score-ring" style={{ '--pct': puntaje }}>
            <span className="score-num">{puntaje}%</span>
          </div>
          <div className="score-meta">
            <strong>{evaluados} de {total} evaluados</strong>
            <div className="score-chips">
              <span className="chip chip-cumple"><b>{counts.cumple}</b> Cumple</span>
              <span className="chip chip-parcial"><b>{counts.parcial}</b> Parcial</span>
              <span className="chip chip-no_cumple"><b>{counts.no_cumple}</b> No cumple</span>
              <span className="chip chip-sin"><b>{counts.sin_evaluar}</b> Sin evaluar</span>
            </div>
          </div>
        </div>
        <div className="quick-actions">
          <button type="button" className="btn ghost sm" onClick={marcarTodoCumple} disabled={total === 0}>Marcar todo cumple</button>
          <button type="button" className="btn ghost sm" onClick={limpiarTodo} disabled={total === 0}>Limpiar</button>
        </div>
      </div>

      {total > 0 && (
        <div className="filtros" role="tablist" aria-label="Filtrar criterios">
          {FILTROS.map((f) => {
            const count = f.key === 'todos' ? total : counts[f.key]
            return (
              <button
                type="button"
                key={f.key}
                role="tab"
                aria-selected={filtro === f.key}
                className={`filtro ${filtro === f.key ? 'active' : ''}`}
                onClick={() => setFiltro(f.key)}
              >
                {f.label} <span className="filtro-count">{count}</span>
              </button>
            )
          })}
        </div>
      )}

      {total === 0 && <p className="vacio">Agrega criterios primero en la pestaña «Criterios».</p>}

      {total > 0 && listaFiltrada.length === 0 && (
        <p className="vacio">No hay criterios con el filtro «{FILTROS.find((f) => f.key === filtro)?.label}».</p>
      )}

      <ul className="lista-evaluacion">
        {listaFiltrada.map((c) => {
          const it = items[c.id] || {}
          const estado = it.estado || null
          const meta = estado ? ESTADOS[estado] : null
          return (
            <li key={c.id} className={`eval-item ${meta ? meta.clase : 'sin'}`}>
              <div className="criterio-header">
                <span className="orden">{String(c.id).padStart(2, '0')}</span>
                <span className="texto">{c.texto}</span>
                {meta && <span className={`badge-estado badge-${meta.clase}`}>{meta.label}</span>}
              </div>

              <div className="eval-controls">
                <fieldset className="seg" aria-label={`Estado del criterio: ${c.texto}`}>
                  <label className="seg-item">
                    <input type="radio" name={`c-${c.id}`} checked={estado === 'cumple'} onChange={() => setEstado(c.id, 'cumple')} />
                    <span className="seg-cumple">Cumple</span>
                  </label>
                  <label className="seg-item">
                    <input type="radio" name={`c-${c.id}`} checked={estado === 'parcial'} onChange={() => setEstado(c.id, 'parcial')} />
                    <span className="seg-parcial">Parcial</span>
                  </label>
                  <label className="seg-item">
                    <input type="radio" name={`c-${c.id}`} checked={estado === 'no_cumple'} onChange={() => setEstado(c.id, 'no_cumple')} />
                    <span className="seg-no_cumple">No cumple</span>
                  </label>
                </fieldset>
                {estado && (
                  <button type="button" className="btn ghost sm" onClick={() => limpiarEstado(c.id)} aria-label="Quitar estado de este criterio">
                    Quitar
                  </button>
                )}
              </div>

              {it.cobertura && (
                <p className="eval-cobertura">
                  Cobertura {it.cobertura}
                  {it.encontrados?.length ? ` · Encontrado: ${it.encontrados.join(', ')}` : ''}
                  {it.faltantes?.length ? ` · Falta: ${it.faltantes.join(', ')}` : ''}
                </p>
              )}

              <textarea
                className="obs"
                rows={2}
                placeholder="Observación (opcional)"
                value={it.observacion || ''}
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

      <div className="eval-footer">
        <div className="eval-footer-inner">
          <button type="button" className="btn primary" onClick={guardar} disabled={total === 0}>Guardar evaluación</button>
          {guardado && (
            <>
              <button type="button" className="btn" onClick={() => nav.reporte(guardado)}>Ver reporte</button>
              <span className="ok">Guardado ✓</span>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
