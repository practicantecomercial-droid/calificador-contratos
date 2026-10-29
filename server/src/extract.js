import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs'
import mammoth from 'mammoth'

async function extraerTextoPdf(buffer) {
  const doc = await getDocument({ data: new Uint8Array(buffer), useSystemFonts: true }).promise
  let texto = ''
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i)
    const content = await page.getTextContent()
    const strings = content.items.map((it) => it.str)
    texto += strings.join(' ') + '\n'
  }
  return texto
}

export async function extraerTexto(buffer, nombreArchivo) {
  const nombre = (nombreArchivo || '').toLowerCase()
  if (nombre.endsWith('.pdf')) {
    return extraerTextoPdf(buffer)
  }
  if (nombre.endsWith('.docx') || nombre.endsWith('.doc')) {
    const result = await mammoth.extractRawText({ buffer })
    return result.value
  }
  throw new Error('Formato no soportado. Usa PDF o Word (.docx/.doc).')
}
