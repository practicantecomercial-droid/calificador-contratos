export default function InicioPage({ onIniciar }) {
  return (
    <div className="inicio">
      <div className="inicio-card">
        <span className="logo">Interdoors</span>
        <h1>Calificador de Contratos</h1>
        <p className="slogan">Creando Hogares</p>
        <p>Lista de chequeo de gestión de contratos de obra</p>
        <button className="btn-iniciar" onClick={onIniciar}>
          Click para iniciar
        </button>
      </div>
    </div>
  )
}
