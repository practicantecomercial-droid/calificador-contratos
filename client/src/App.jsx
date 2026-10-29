import { useState } from 'react'
import InicioPage from './components/InicioPage.jsx'
import CriteriosPage from './components/CriteriosPage.jsx'
import EvaluarPage from './components/EvaluarPage.jsx'
import HistorialPage from './components/HistorialPage.jsx'
import ReportePage from './components/ReportePage.jsx'

export default function App() {
  const [view, setView] = useState({ name: 'inicio' })

  const nav = {
    inicio: () => setView({ name: 'inicio' }),
    criterios: () => setView({ name: 'criterios' }),
    evaluar: (id) => setView({ name: 'evaluar', id }),
    historial: () => setView({ name: 'historial' }),
    reporte: (id) => setView({ name: 'reporte', id })
  }

  if (view.name === 'inicio') {
    return <InicioPage onIniciar={nav.criterios} />
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1 onClick={nav.inicio}>Calificador de Contratos</h1>
        <nav>
          <button className={view.name === 'criterios' ? 'active' : ''} onClick={nav.criterios}>Criterios</button>
          <button className={view.name === 'evaluar' ? 'active' : ''} onClick={() => nav.evaluar()}>Evaluar</button>
          <button className={view.name === 'historial' ? 'active' : ''} onClick={nav.historial}>Historial</button>
        </nav>
      </header>

      <main>
        {view.name === 'criterios' && <CriteriosPage />}
        {view.name === 'evaluar' && <EvaluarPage id={view.id} nav={nav} />}
        {view.name === 'historial' && <HistorialPage nav={nav} />}
        {view.name === 'reporte' && <ReportePage id={view.id} nav={nav} />}
      </main>
    </div>
  )
}
