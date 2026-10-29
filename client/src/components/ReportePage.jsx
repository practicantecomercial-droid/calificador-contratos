import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function ReportePage({ id, nav }) {
  const [ev, setEv] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function cargar() {
      try {
        const data = await api.obtenerEvaluacion(id)
        setEv(data)
      } catch (e) {
        setError(e.message)
      }
    }
    cargar()
  }, [id])

  if (error) return <div className="page"><h2>Reporte</h2><p className="error">{error}</p></div>
  if (!ev) return <div className="page"><h2>Reporte</h2><p>Cargando…</p></div>

  const total = ev.items.length
  const cumplidos = ev.items.filter((i) => i.cumple).length
  const porcentaje = total === 0 ? 0 : Math.round((cumplidos / total) * 100)

  return (
    <div className="page">
      <div className="no-print">
        <button className="btn" onClick={() => window.print()}>Imprimir / Guardar PDF</button>
        <button className="btn" onClick={() => nav.historial()}>Volver</button>
      </div>

      <div className="reporte">
        <header className="reporte-header">
          <h1>Reporte de Evaluación de Contrato</h1>
          <h2>{ev.nombre_contrato}</h2>
          <p className="fecha">Fecha: {ev.fecha}</p>
        </header>

        <div className="reporte-resumen">
          <div className="resumen-box">
            <span className="cifra">{porcentaje}%</span>
            <span className="etiqueta">de cumplimiento</span>
          </div>
          <div className="resumen-box">
            <span className="cifra">{cumplidos}/{total}</span>
            <span className="etiqueta">criterios cumplidos</span>
          </div>
        </div>

        <table className="reporte-tabla">
          <thead>
            <tr>
              <th className="col-n">#</th>
              <th>Criterio</th>
              <th className="col-estado">Estado</th>
              <th className="col-obs">Observación</th>
            </tr>
          </thead>
          <tbody>
            {ev.items.map((it, i) => (
              <tr key={i} className={it.cumple ? 'cumple' : 'no-cumple'}>
                <td className="col-n">{i + 1}</td>
                <td>{it.criterio_texto}</td>
                <td className="col-estado">{it.cumple ? 'Cumple' : 'No cumple'}</td>
                <td className="col-obs">{it.observacion || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {ev.observacion_general && (
          <div className="reporte-general">
            <h3>Observaciones generales</h3>
            <p>{ev.observacion_general}</p>
          </div>
        )}
      </div>
    </div>
  )
}
