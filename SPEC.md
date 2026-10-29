# Spec: Calificador de Contratos

## Objective
Una aplicación web de uso personal para calificar contratos mediante una lista de chequeo
de criterios tipo Sí/No. El usuario revisa un contrato, marca cada criterio como cumplido o
no, añade observaciones, y obtiene un puntaje (porcentaje de cumplimiento y "X de N").
Cada evaluación se guarda en un historial para consultarla, reabrirla o eliminarla, y se
puede generar un reporte imprimible (PDF vía impresión del navegador).

**Usuario:** una sola persona (sin autenticación ni multiusuario).
**Éxito:** crear criterios, evaluar contratos, ver puntaje, guardar historial y exportar reporte.

## Tech Stack
- Backend: Node.js + Express, base de datos SQLite (módulo nativo `node:sqlite`, sin dependencias nativas compiladas).
- Frontend: React + Vite (JavaScript, no TypeScript, para reducir fricción).
- Sin framework CSS pesado: estilos propios en CSS simple.
- Reporte: vista imprimible (media print) → "Guardar como PDF" del navegador.

## Commands
```
Instalar backend:  npm install        (en server/)
Correr backend:    npm run dev        (en server/, puerto 3001)
Instalar frontend: npm install        (en client/)
Correr frontend:   npm run dev        (en client/, puerto 5173)
Build frontend:    npm run build      (en client/)
```

## Project Structure
```
calificador-contratos/
├── SPEC.md
├── tasks/
│   ├── plan.md
│   └── todo.md
├── server/                 → API Express + SQLite
│   ├── package.json
│   ├── src/
│   │   ├── index.js        → punto de entrada del servidor
│   │   ├── db.js           → conexión y esquema SQLite
│   │   └── routes.js       → rutas REST
│   └── data/               → archivo .db (gitignored)
└── client/                 → frontend React + Vite
    ├── package.json
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api.js          → cliente HTTP hacia el backend
        ├── components/
        │   ├── CriteriosPage.jsx
        │   ├── EvaluarPage.jsx
        │   ├── HistorialPage.jsx
        │   └── ReportePage.jsx
        └── styles.css
```

## Code Style
- JavaScript moderno (ESM). Funciones de flecha, `const`/`let`.
- Nombres en español para conceptos de dominio (`criterio`, `evaluacion`), inglés para código genérico.
- Sin punto y coma al final (estilo semicolon-less).
- Componentes React funcionales con hooks.
- Ejemplo:
```js
export async function listarCriterios() {
  const res = await fetch('/api/criterios')
  return res.json()
}
```

## Testing Strategy
- Framework: pruebas de humo manuales + script de verificación de endpoints (`curl`).
- Cobertura: validar los endpoints CRUD de criterios y evaluaciones.
- No se exige cobertura automatizada en esta primera versión (app de uso personal).

## Boundaries
- Always: mantener el esquema SQLite versionado en `db.js`; validar entradas en el servidor; correr el servidor y el cliente para verificar antes de dar por terminada una tarea.
- Ask first: cambiar el stack (lenguaje/framework/base de datos); agregar autenticación o multiusuario; agregar dependencias nuevas.
- Never: commitear secretos; borrar el historial sin confirmación del usuario; guardar archivos fuera de `server/data/`.

## Data Model
- `criterios`: id, texto, activo (bool), orden (int).
- `evaluaciones`: id, nombre_contrato, fecha, observacion_general.
- `evaluacion_items`: id, evaluacion_id, criterio_id, cumple (bool), observacion.

## Success Criteria
- [ ] Crear/editar/ordenar/eliminar criterios de la lista de chequeo.
- [ ] Evaluar un contrato marcando Sí/No por criterio con observaciones por ítem.
- [ ] Mostrar puntaje en vivo: porcentaje de cumplimiento y "X de N cumplidos".
- [ ] Guardar la evaluación con nombre de contrato y fecha.
- [ ] Ver historial de evaluaciones y reabrir o eliminar cualquiera.
- [ ] Generar reporte imprimible/PDF con detalle por criterio y resumen final.

## Open Questions
- ¿Los criterios tienen pesos o todos valen igual? (asumido: todos valen igual).
- ¿El checklist es un único conjunto de criterios, o hay varias plantillas? (asumido: un único conjunto).
