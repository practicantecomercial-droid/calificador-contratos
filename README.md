# Calificador de Contratos

App web para calificar contratos con una lista de chequeo tipo Sí/No, guardar historial y generar reportes imprimibles (PDF).

## Requisitos
- Node.js 24 o superior (usa el módulo nativo `node:sqlite`… no, usa archivo JSON, así que sirve cualquier Node 18+).

## Instalación

### Backend
```bash
cd server
npm install
npm run dev      # http://localhost:3001
```

### Frontend
```bash
cd client
npm install
npm run dev      # http://localhost:5173
```

Abre http://localhost:5173 en el navegador.

## Uso
0. **Inicio**: pantalla de bienvenida con "Click para iniciar".
1. **Criterios**: crea, ordena, edita o elimina los criterios de tu lista de chequeo.
2. **Evaluar**: llena el nombre del contrato, marca Sí/No por criterio, añade observaciones. El puntaje (% y "X de N") se actualiza en vivo. Guarda.
3. **Historial**: consulta, reabre o elimina evaluaciones guardadas.
4. **Reporte**: desde Historial o tras guardar, abre el reporte y usa "Imprimir / Guardar PDF".

## Cargar documento y analizar con IA
En la pantalla **Evaluar** puedes cargar el contrato (PDF o Word):

- **Analizar con IA (OpenAI)**: la IA lee el documento, lo compara contra los 25 criterios y marca automáticamente Cumple/No cumple con una justificación. Luego tú revisas y guardas.
- **Analizar local (sin IA)**: un script local busca palabras clave de cada criterio dentro del documento y marca Cumple/No cumple con lo que encontró. No requiere internet ni clave de OpenAI.
- **Revisar manualmente**: muestra el texto extraído del documento y tú marcas los criterios a mano.

Para activar la IA, agrega tu clave de OpenAI en `server/.env`:
```
OPENAI_API_KEY=sk-...
```
(consíguela en https://platform.openai.com/api-keys). Por defecto usa `gpt-4o-mini`.

## Datos
La información se guarda en `server/data/data.json` (archivo JSON, sin base de datos externa). Puedes respaldar ese archivo para conservar tu historial.

Los 25 criterios de la lista de chequeo de gestión de contratos (Interdoors) ya vienen precargados. Para regenerarlos en una instalación nueva:
```bash
cd server
npm run seed
```

## Estructura
- `server/` — API Express (rutas y persistencia en JSON).
- `client/` — frontend React + Vite.
- `SPEC.md` — especificación.
- `tasks/` — plan y tareas.

## Despliegue en Render
El repo incluye `render.yaml` (blueprint). En Render: **New → Blueprint** y elige este repo; se crea un Web Service gratis que compila el frontend y arranca el backend. La URL será del tipo `https://calificador-contratos.onrender.com`.

- Los 25 criterios se siembran automáticamente en el primer arranque.
- La clave de OpenAI se configura como variable de entorno `OPENAI_API_KEY` (opcional).
- Nota: el plan gratuito usa disco efímero, así que el historial se reinicia en cada redeploy.
