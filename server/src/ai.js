import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const envFile = join(__dirname, '..', '.env')
if (existsSync(envFile)) {
  process.loadEnvFile(envFile)
}

export function apiKeyDisponible() {
  return Boolean(process.env.OPENAI_API_KEY)
}

export async function analizarConIA(texto, criterios) {
  const apiKey = process.env.OPENAI_API_KEY
  if (!apiKey) {
    throw new Error('Falta OPENAI_API_KEY. Agrega tu clave en server/.env (OPENAI_API_KEY=sk-...)')
  }

  const modelo = process.env.OPENAI_MODEL || 'gpt-4o-mini'

  const listaCriterios = criterios.map((c) => `${c.id}. ${c.texto}`).join('\n')

  const maxChars = 120000
  const textoRecortado =
    texto.length > maxChars ? texto.slice(0, maxChars) + '\n…[documento recortado]' : texto

  const sistema = `Eres un analista experto en contratos de obra y carpintería. Evalúa un documento de contrato contra una lista de criterios de gestión de contratos. Para cada criterio indica si se CUMPLE (true) o NO (false) según lo que esté expresamente escrito en el documento, y da una justificación breve y concreta (máx 20 palabras). Si el criterio no se puede verificar en el documento, responde false y justifica "No se evidencia en el documento". Responde SOLO con un JSON válido con la forma: {"resultados":[{"criterio_id":1,"cumple":true,"justificacion":"texto"}]}.`

  const usuario = `Criterios a evaluar:\n${listaCriterios}\n\nDocumento del contrato:\n${textoRecortado}`

  const resp = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: modelo,
      temperature: 0,
      response_format: { type: 'json_object' },
      messages: [
        { role: 'system', content: sistema },
        { role: 'user', content: usuario }
      ]
    })
  })

  if (!resp.ok) {
    const err = await resp.text().catch(() => '')
    throw new Error(`Error de OpenAI (${resp.status}): ${err.slice(0, 300)}`)
  }

  const data = await resp.json()
  const contenido = data.choices?.[0]?.message?.content
  if (!contenido) throw new Error('Respuesta vacía de OpenAI')

  const parsed = JSON.parse(contenido)
  return parsed.resultados || parsed
}
