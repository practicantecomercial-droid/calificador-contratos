# Tareas

- [ ] T1: Backend — esquema SQLite y conexión
  - Acceptance: `db.js` inicializa la BD con tablas criterios, evaluaciones, evaluacion_items.
  - Verify: `node -e "require('./src/db.js')"` crea el archivo sin errores.
  - Files: server/src/db.js, server/package.json

- [ ] T2: Backend — rutas REST
  - Acceptance: CRUD criterios + CRUD evaluaciones (con items) responden correctamente.
  - Verify: `curl` a cada endpoint devuelve JSON esperado.
  - Files: server/src/routes.js, server/src/index.js

- [ ] T3: Frontend — scaffold Vite + cliente HTTP
  - Acceptance: app React corre con proxy al backend; `api.js` con funciones para cada endpoint.
  - Verify: `npm run dev` arranca y muestra pantalla base.
  - Files: client/package.json, client/vite.config.js, client/index.html, client/src/main.jsx, client/src/App.jsx, client/src/api.js

- [ ] T4: Frontend — página de Criterios
  - Acceptance: listar, crear, editar, reordenar y eliminar criterios.
  - Verify: operaciones CRUD desde la UI se reflejan en el backend.
  - Files: client/src/components/CriteriosPage.jsx

- [ ] T5: Frontend — página Evaluar
  - Acceptance: formulario con Sí/No por criterio, observaciones, puntaje en vivo (% y X de N), guardar.
  - Verify: guardar crea evaluación y redirige/persiste.
  - Files: client/src/components/EvaluarPage.jsx

- [ ] T6: Frontend — página Historial
  - Acceptance: listar evaluaciones, reabrir (editar) y eliminar.
  - Verify: reabrir carga datos; eliminar los quita de la lista y la BD.
  - Files: client/src/components/HistorialPage.jsx

- [ ] T7: Frontend — Reporte imprimible
  - Acceptance: vista de reporte por evaluación con resumen y detalle, estilos print.
  - Verify: imprimir/guardar PDF muestra el detalle completo.
  - Files: client/src/components/ReportePage.jsx
