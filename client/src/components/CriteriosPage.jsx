import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function CriteriosPage() {
  const [criterios, setCriterios] = useState([])
  const [nuevo, setNuevo] = useState('')
  const [editando, setEditando] = useState(null)
  const [editTexto, setEditTexto] = useState('')
  const [cargando, setCargando] = useState(true)

  async function cargar() {
    setCargando(true)
    const data = await api.listarCriterios()
    setCriterios(data)
    setCargando(false)
  }

  useEffect(() => { cargar() }, [])

  async function agregar(e) {
    e.preventDefault()
    if (!nuevo.trim()) return
    await api.crearCriterio(nuevo)
    setNuevo('')
    cargar()
  }

  async function guardarEdicion(id) {
    if (!editTexto.trim()) return
    await api.editarCriterio(id, editTexto)
    setEditando(null)
    cargar()
  }

  async function eliminar(id) {
    if (!window.confirm('¿Eliminar este criterio?')) return
    await api.eliminarCriterio(id)
    cargar()
  }

  async function mover(index, dir) {
    const destino = index + dir
    if (destino < 0 || destino >= criterios.length) return
    const nueva = [...criterios]
    const [item] = nueva.splice(index, 1)
    nueva.splice(destino, 0, item)
    setCriterios(nueva)
    for (let i = 0; i < nueva.length; i++) {
      await api.reordenarCriterio(nueva[i].id, i)
    }
  }

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h2>Lista de chequeo</h2>
          <p className="page-sub">Estos son los criterios que se evalúan en cada contrato. Puedes agregarlos, editarlos y reordenarlos.</p>
        </div>
        <span className="tag tag-count">{criterios.length} criterios</span>
      </div>

      <form className="form-inline" onSubmit={agregar}>
        <input
          type="text"
          value={nuevo}
          onChange={(e) => setNuevo(e.target.value)}
          placeholder="Nuevo criterio…"
          aria-label="Nuevo criterio"
        />
        <button type="submit" className="btn primary" disabled={!nuevo.trim()}>Agregar</button>
      </form>

      {cargando ? (
        <ul className="lista-criterios" aria-busy="true" aria-label="Cargando criterios">
          {[0, 1, 2, 3].map((i) => <li key={i} className="skeleton-row" />)}
        </ul>
      ) : (
        <ul className="lista-criterios">
          {criterios.map((c, i) => (
            <li key={c.id}>
              {editando === c.id ? (
                <>
                  <span className="orden">{i + 1}.</span>
                  <input
                    type="text"
                    value={editTexto}
                    onChange={(e) => setEditTexto(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && guardarEdicion(c.id)}
                    aria-label={`Editar criterio ${i + 1}`}
                  />
                  <button type="button" className="btn primary sm" onClick={() => guardarEdicion(c.id)}>Guardar</button>
                  <button type="button" className="btn ghost sm" onClick={() => setEditando(null)}>Cancelar</button>
                </>
              ) : (
                <>
                  <span className="orden">{i + 1}.</span>
                  <span className="texto">{c.texto}</span>
                </>
              )}
              <span className="acciones">
                {editando !== c.id && (
                  <>
                    <button type="button" className="btn icon sm" onClick={() => mover(i, -1)} disabled={i === 0} aria-label="Subir criterio">↑</button>
                    <button type="button" className="btn icon sm" onClick={() => mover(i, 1)} disabled={i === criterios.length - 1} aria-label="Bajar criterio">↓</button>
                    <button type="button" className="btn sm" onClick={() => { setEditando(c.id); setEditTexto(c.texto) }}>Editar</button>
                    <button type="button" className="btn danger sm" onClick={() => eliminar(c.id)}>Eliminar</button>
                  </>
                )}
              </span>
            </li>
          ))}
        </ul>
      )}

      {!cargando && criterios.length === 0 && (
        <div className="empty-state">
          <h3>No hay criterios todavía</h3>
          <p>Agrega el primer criterio con el formulario de arriba.</p>
        </div>
      )}
    </div>
  )
}
