import express from 'express'
import cors from 'cors'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { existsSync } from 'node:fs'
import routes from './routes.js'
import { sembrarCriterios } from './seed.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const app = express()
const PORT = process.env.PORT || 3001

const sembrados = sembrarCriterios()
if (sembrados > 0) console.log(`Se sembraron ${sembrados} criterios.`)

app.use(cors())
app.use(express.json())
app.use('/api', routes)

const distDir = join(__dirname, '..', '..', 'client', 'dist')
if (existsSync(distDir)) {
  app.use(express.static(distDir))
  app.get(/^\/(?!api).*/, (req, res) => {
    res.sendFile(join(distDir, 'index.html'))
  })
}

app.listen(PORT, () => {
  console.log(`Calificador de Contratos listo en http://localhost:${PORT}`)
})
