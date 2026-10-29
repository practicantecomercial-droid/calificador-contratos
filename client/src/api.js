async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.error || `Error ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  // Criterios
  listarCriterios: () => request('/api/criterios'),
  crearCriterio: (texto) => request('/api/criterios', { method: 'POST', body: JSON.stringify({ texto }) }),
  editarCriterio: (id, texto) => request(`/api/criterios/${id}`, { method: 'PUT', body: JSON.stringify({ texto }) }),
  reordenarCriterio: (id, orden) => request(`/api/criterios/${id}/orden`, { method: 'PUT', body: JSON.stringify({ orden }) }),
  eliminarCriterio: (id) => request(`/api/criterios/${id}`, { method: 'DELETE' }),

  // Evaluaciones
  listarEvaluaciones: () => request('/api/evaluaciones'),
  obtenerEvaluacion: (id) => request(`/api/evaluaciones/${id}`),
  crearEvaluacion: (payload) => request('/api/evaluaciones', { method: 'POST', body: JSON.stringify(payload) }),
  editarEvaluacion: (id, payload) => request(`/api/evaluaciones/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  eliminarEvaluacion: (id) => request(`/api/evaluaciones/${id}`, { method: 'DELETE' }),

  // Documento e IA
  extraerDocumento: async (file) => {
    const fd = new FormData()
    fd.append('documento', file)
    const res = await fetch('/api/extraer', { method: 'POST', body: fd })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.error || `Error ${res.status}`)
    }
    return res.json()
  },
  iaDisponible: () => request('/api/ia/disponible'),
  analizarConIA: (texto, criterios) => request('/api/analizar', { method: 'POST', body: JSON.stringify({ texto, criterios }) }),
  analizarLocal: (texto, criterios) => request('/api/analizar-local', { method: 'POST', body: JSON.stringify({ texto, criterios }) })
}
