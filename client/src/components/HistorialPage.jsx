import { useEffect, useState } from 'react'
import { api } from '../api.js'

function fechaBonita(f) {
  if (!f) return ''
  const d = new Date(f + 'T00:00:00')
  if (Number.isNaN(d.getTime())) return f
  return d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

export default function HistorialPage({ nav }) {
  const [evaluaciones, setEvaluaciones] = useState([])
  const [cargando, setCargando] = useState(true)

  async function cargar() {
    setCargando(true)
    try {
      const data = await api.listarEvaluaciones()
      setEvaluaciones(data)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => { cargar() }, [])

  async function eliminar(id) {
    if (!window.confirm('¿Eliminar esta evaluación? Esta acción no se puede deshacer.')) return
    await api.eliminarEvaluacion(id)
    cargar()
  }

  function porcentaje(ev) {
    if (typeof ev.puntaje === 'number') return ev.puntaje
    return ev.total === 0 ? 0 : Math.round((ev.cumplidos / ev.total) * 100)
  }

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h2>Historial de evaluaciones</h2>
          <p className="page-sub">Consulta, edita o genera el reporte de cada evaluación guardada.</p>
        </div>
        <button type="button" className="btn primary" onClick={() => nav.evaluar()}>Nueva evaluación</button>
      </div>

      {cargando ? (
        <ul className="lista-historial" aria-busy="true" aria-label="Cargando evaluaciones">
          {[0, 1, 2].map((i) => <li key={i} className="skeleton-row" />)}
        </ul>
      ) : evaluaciones.length === 0 ? (
        <div className="empty-state">
          <h3>Sin evaluaciones todavía</h3>
          <p>Cuando guardes una evaluación aparecerá aquí con su puntaje y estado.</p>
          <button type="button" className="btn primary" onClick={() => nav.evaluar()}>Crear la primera</button>
        </div>
      ) : (
        <ul className="lista-historial">
          {evaluaciones.map((ev) => {
            const pct = porcentaje(ev)
            const parciales = ev.parciales || 0
            const noCumple = ev.no_cumple || 0
            const sinEval = ev.sin_evaluar || 0
            const wCumple = ev.total ? (ev.cumplidos / ev.total) * 100 : 0
            const wParcial = ev.total ? (parciales / ev.total) * 100 : 0
            return (
              <li key={ev.id} className="historial-card">
                <div className="historial-info">
                  <strong className="historial-nombre">{ev.nombre_contrato}</strong>
                  <span className="fecha">{fechaBonita(ev.fecha)}</span>
                  <div className="bar" aria-hidden="true">
                    <span className="bar-cumple" style={{ width: `${wCumple}%` }} />
                    <span className="bar-parcial" style={{ width: `${wParcial}%` }} />
                  </div>
                  <div className="historial-chips">
                    <span className="chip chip-cumple"><b>{ev.cumplidos}</b> cumple</span>
                    <span className="chip chip-parcial"><b>{parciales}</b> parcial</span>
                    <span className="chip chip-no_cumple"><b>{noCumple}</b> no cumple</span>
                    {sinEval > 0 && <span className="chip chip-sin"><b>{sinEval}</b> sin evaluar</span>}
                  </div>
                </div>
                <div className="historial-lado">
                  <span className="historial-pct">{pct}%</span>
                  <span className="acciones">
                    <button type="button" className="btn sm" onClick={() => nav.evaluar(ev.id)}>Editar</button>
                    <button type="button" className="btn sm" onClick={() => nav.reporte(ev.id)}>Reporte</button>
                    <button type="button" className="btn danger sm" onClick={() => eliminar(ev.id)}>Eliminar</button>
                  </span>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
