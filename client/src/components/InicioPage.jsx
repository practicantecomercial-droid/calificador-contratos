export default function InicioPage({ onIniciar }) {
  return (
    <div className="inicio">
      <div className="inicio-card">
        <h1>Calificador de Contratos</h1>
        <p>Lista de chequeo de gestión de contratos de obra — Interdoors</p>
        <button className="btn-iniciar" onClick={onIniciar}>
          Click para iniciar
        </button>
      </div>
    </div>
  )
}
