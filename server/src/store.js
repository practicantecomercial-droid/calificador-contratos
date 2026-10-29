import { mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const dataDir = join(__dirname, '..', 'data')
const dataFile = join(dataDir, 'data.json')

const empty = { criterios: [], evaluaciones: [] }

function readData() {
  if (!existsSync(dataFile)) {
    mkdirSync(dataDir, { recursive: true })
    writeFileSync(dataFile, JSON.stringify(empty, null, 2))
    return structuredClone(empty)
  }
  const raw = readFileSync(dataFile, 'utf8').replace(/^\uFEFF/, '')
  return JSON.parse(raw)
}

function writeData(data) {
  writeFileSync(dataFile, JSON.stringify(data, null, 2))
}

function nextId(rows) {
  return rows.reduce((m, r) => Math.max(m, r.id), 0) + 1
}

export { readData, writeData, nextId, dataFile }
