import test from 'node:test'
import assert from 'node:assert'
import { normalizarTexto, extraerPorcentajes, extraerPlazos, normalizarUnidad } from '../src/normalizar.js'
import { analizarLocal } from '../src/local.js'

test('normalizarTexto quita tildes y mayúsculas', () => {
  assert.equal(normalizarTexto('PÓLIZA DE CUMPLIMIENTO'), 'poliza de cumplimiento')
  assert.equal(normalizarTexto('GESTIÓN'), 'gestion')
})

test('extraerPorcentajes reconoce dígitos y letras', () => {
  const r = extraerPorcentajes('anticipo 40% y cuarenta por ciento. Ret Anticipo 30%')
  assert.ok(r.includes(40), 'debe detectar 40%')
  assert.ok(r.includes(30), 'debe detectar 30%')
})

test('extraerPlazos reconoce plazos en dígitos y letras', () => {
  const p = extraerPlazos('vigencia mínima de tres (3) años y 30 dias de credito')
  assert.ok(p.some((x) => x.valor === 3 && x.unidad === 'años'))
  assert.ok(p.some((x) => x.valor === 30 && x.unidad === 'dias'))
})

test('normalizarUnidad unifica variantes', () => {
  assert.equal(normalizarUnidad('años'), 'años')
  assert.equal(normalizarUnidad('anos'), 'años')
  assert.equal(normalizarUnidad('dias'), 'dias')
  assert.equal(normalizarUnidad('meses'), 'meses')
})

test('analizarLocal: contrato con 2 pólizas da "parcial" en Pólizas', () => {
  const criterios = [
    { id: 9, texto: 'Pólizas' },
    { id: 2, texto: 'Forma de pago' }
  ]
  const texto = 'POLIZA DE BUEN MANEJO DE ANTICIPO 30%. POLIZA DE CUMPLIMIENTO 20%. Ret Anticipo 30%.'
  const res = analizarLocal(texto, criterios)

  const p9 = res.find((r) => r.criterio_id === 9)
  assert.equal(p9.estado, 'parcial')
  assert.ok(p9.faltantes.includes('Responsabilidad civil'))

  const p2 = res.find((r) => r.criterio_id === 2)
  assert.equal(p2.estado, 'no_cumple', 'no debe marcar forma de pago solo por "anticipo 30%"')
})

test('analizarLocal: texto con forma de pago completa da "cumple"', () => {
  const criterios = [{ id: 2, texto: 'Forma de pago' }]
  const texto = 'Anticipo del 40% y saldo del 60% contra entrega.'
  const res = analizarLocal(texto, criterios)
  assert.equal(res[0].estado, 'cumple')
})

test('analizarLocal: criterio sin config usa palabras del propio criterio', () => {
  const criterios = [{ id: 999, texto: 'Validar póliza de responsabilidad civil extracontractual' }]
  const res = analizarLocal('se presenta poliza de responsabilidad civil', criterios)
  assert.equal(res[0].estado, 'cumple')
})
