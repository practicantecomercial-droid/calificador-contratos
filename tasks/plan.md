# Plan: Calificador de Contratos

## Componentes y orden de implementación

1. **Backend (server/)** — API Express + SQLite. Es la base sobre la que depende el frontend.
   - `db.js`: conexión SQLite + esquema (tablas criterios, evaluaciones, evaluacion_items).
   - `routes.js`: CRUD de criterios y evaluaciones.
   - `index.js`: servidor Express con JSON + CORS para el frontend de Vite.
2. **Frontend (client/)** — React + Vite.
   - `api.js`: cliente HTTP.
   - `CriteriosPage`: gestionar la lista de chequeo.
   - `EvaluarPage`: evaluar contrato con puntaje en vivo.
   - `HistorialPage`: listar/reabrir/eliminar evaluaciones.
   - `ReportePage`: reporte imprimible.

## Orden (secuencial)
Backend primero (schema + rutas) → cliente HTTP → pantallas (Criterios → Evaluar → Historial → Reporte).

## Riesgos y mitigación
- `node:sqlite` es relativamente nuevo → verificar disponibilidad en Node 24; si falla, usar `better-sqlite3`.
- CORS entre Vite (5173) y Express (3001) → habilitar CORS en el backend y proxy en Vite.
- Impresión a PDF depende del navegador → usar estilos `@media print` y probar en Chrome.

## Puntos de verificación
- Tras el backend: probar endpoints con `curl`.
- Tras cada pantalla: levantar cliente+servidor y verificar en navegador.
