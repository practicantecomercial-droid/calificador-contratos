import { useEffect, useState } from 'react'
import { api } from '../api.js'

const ESTADOS = {
  cumple: { label: 'Cumple', clase: 'cumple' },
  parcial: { label: 'Parcial', clase: 'parcial' },
  no_cumple: { label: 'No cumple', clase: 'no_cumple' },
  sin_evaluar: { label: 'Sin evaluar', clase: 'sin' }
}

function estadoDe(it) {
  return ESTADOS[it.estado] ? it.estado : (it.cumple ? 'cumple' : 'no_cumple')
}

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
  const counts = { cumple: 0, parcial: 0, no_cumple: 0, sin_evaluar: 0 }
  for (const it of ev.items) counts[estadoDe(it)] += 1
  const puntaje = total === 0 ? 0 : Math.round(((counts.cumple + 0.5 * counts.parcial) / total) * 100)

  return (
    <div className="page">
      <div className="no-print reporte-acciones">
        <button type="button" className="btn primary" onClick={() => window.print()}>Imprimir / Guardar PDF</button>
        <button type="button" className="btn" onClick={() => nav.historial()}>Volver al historial</button>
      </div>

      <div className="reporte">
        <header className="reporte-header">
          <span className="reporte-logo">Interdoors</span>
          <h1>Reporte de Evaluación de Contrato</h1>
          <h2>{ev.nombre_contrato}</h2>
          <p className="fecha">Fecha: {ev.fecha}</p>
        </header>

        <div className="reporte-resumen">
          <div className="resumen-box resumen-box--score">
            <span className="cifra">{puntaje}%</span>
            <span className="etiqueta">puntaje de cumplimiento</span>
          </div>
          <div className="resumen-box">
            <span className="cifra cifra-cumple">{counts.cumple}</span>
            <span className="etiqueta">cumple</span>
          </div>
          <div className="resumen-box">
            <span className="cifra cifra-parcial">{counts.parcial}</span>
            <span className="etiqueta">parcial</span>
          </div>
          <div className="resumen-box">
            <span className="cifra cifra-no">{counts.no_cumple}</span>
            <span className="etiqueta">no cumple</span>
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
            {ev.items.map((it, i) => {
              const estado = estadoDe(it)
              return (
                <tr key={i} className={estado}>
                  <td className="col-n">{i + 1}</td>
                  <td>{it.criterio_texto}</td>
                  <td className="col-estado">{ESTADOS[estado].label}</td>
                  <td className="col-obs">{it.observacion || '—'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>

        {ev.observacion_general && (
          <div className="reporte-general">
            <h3>Observaciones generales</h3>
            <p>{ev.observacion_general}</p>
          </div>
        )}

        <footer className="reporte-pie">
          <span>Calificador de Contratos · Interdoors</span>
          <span>Creando Hogares</span>
        </footer>
      </div>
    </div>
  )
}
