import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function HistorialPage({ nav }) {
  const [evaluaciones, setEvaluaciones] = useState([])
  const [cargando, setCargando] = useState(true)

  async function cargar() {
    setCargando(true)
    const data = await api.listarEvaluaciones()
    setEvaluaciones(data)
    setCargando(false)
  }

  useEffect(() => { cargar() }, [])

  async function eliminar(id) {
    if (!window.confirm('¿Eliminar esta evaluación? Esta acción no se puede deshacer.')) return
    await api.eliminarEvaluacion(id)
    cargar()
  }

  function porcentaje(ev) {
    return ev.total === 0 ? 0 : Math.round((ev.cumplidos / ev.total) * 100)
  }

  return (
    <div className="page">
      <h2>Historial de evaluaciones</h2>

      {cargando ? <p>Cargando…</p> : (
        <>
          {evaluaciones.length === 0 && <p className="vacio">No hay evaluaciones guardadas todavía.</p>}
          <ul className="lista-historial">
            {evaluaciones.map((ev) => (
              <li key={ev.id}>
                <div className="historial-info">
                  <strong>{ev.nombre_contrato}</strong>
                  <span className="fecha">{ev.fecha}</span>
                  <span className="puntaje">{ev.cumplidos}/{ev.total} ({porcentaje(ev)}%)</span>
                </div>
                <span className="acciones">
                  <button className="btn" onClick={() => nav.evaluar(ev.id)}>Editar</button>
                  <button className="btn" onClick={() => nav.reporte(ev.id)}>Reporte</button>
                  <button className="btn danger" onClick={() => eliminar(ev.id)}>Eliminar</button>
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
