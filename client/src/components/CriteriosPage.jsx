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
      <h2>Lista de chequeo</h2>
      <form className="form-inline" onSubmit={agregar}>
        <input
          type="text"
          value={nuevo}
          onChange={(e) => setNuevo(e.target.value)}
          placeholder="Nuevo criterio…"
        />
        <button type="submit" className="btn primary">Agregar</button>
      </form>

      {cargando ? <p>Cargando…</p> : (
        <ul className="lista-criterios">
          {criterios.map((c, i) => (
            <li key={c.id}>
              {editando === c.id ? (
                <>
                  <input
                    type="text"
                    value={editTexto}
                    onChange={(e) => setEditTexto(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && guardarEdicion(c.id)}
                  />
                  <button className="btn" onClick={() => guardarEdicion(c.id)}>Guardar</button>
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
                    <button className="btn" onClick={() => mover(i, -1)} disabled={i === 0}>↑</button>
                    <button className="btn" onClick={() => mover(i, 1)} disabled={i === criterios.length - 1}>↓</button>
                    <button className="btn" onClick={() => { setEditando(c.id); setEditTexto(c.texto) }}>Editar</button>
                    <button className="btn danger" onClick={() => eliminar(c.id)}>Eliminar</button>
                  </>
                )}
              </span>
            </li>
          ))}
          {criterios.length === 0 && <p className="vacio">No hay criterios todavía. Agrega el primero.</p>}
        </ul>
      )}
    </div>
  )
}
