import { readData, writeData } from './store.js'

const TEXTO_CRITERIOS = [
  'Documentos del asesor comercial: dos (2) copias físicas del contrato, carta de no siniestro (constructoras), cotización firmada y actualizada con costeo detallado, y anexos (manual del contratista, documentación SST).',
  'Forma de pago: anticipo del 40%, saldo del 60% contra entrega, amortización proporcional del anticipo y crédito de 30 días solo si el cliente cumple los requisitos.',
  'Independencia de suministro e instalación: cada concepto se factura y cobra de manera separada.',
  'Facturación del suministro: se realiza en el momento de la entrega en obra (parcial o total).',
  'Facturación de la instalación: mediante cortes semanales con base en la entrega efectuada en obra.',
  'Cotización: coincide en precios y cantidades con el contrato; vigencia de treinta (30) días y verificación previa de precios.',
  'Referencia a la cotización: el contrato indica su número consecutivo y fecha de elaboración.',
  'Multas y cláusulas penales: solo bilaterales y equitativas (no unilaterales).',
  'Pólizas: cumplimiento, buen manejo, salarios (mín. 3 años), calidad (mín. 12 meses) y responsabilidad civil; la suma no supera el 100% del valor del contrato.',
  'Ajuste de valores por demora en la ejecución (por causas ajenas a Interdoors).',
  'Documentos para la liquidación de la obra indicados expresamente en el contrato.',
  'Devolución del retenido: requisitos, documentos, plazos y condiciones indicados.',
  'Reajuste por ejecución en vigencia posterior al año de la cotización.',
  'Términos y condiciones de garantía anexos al contrato (alcance, vigencia y procedimiento).',
  'Revisión y aprobación del contrato por el director comercial (firma de validación).',
  'Requisitos para la firma de gerencia: dos (2) copias, firmadas por el director comercial y cotizaciones anexas.',
  'Gestión documental: documentos escaneados y guardados con nomenclatura (asesor, constructora, obra).',
  'Actualización de la relación de contratos en la bitácora (días 15 y 30) con firma del gerente general.',
  'Solicitud de anticipo y pólizas al analista de cartera y jefe administrativo.',
  'Firma y gestión de pólizas por gerencia y archivo en la bitácora.',
  'Entrega de documentos al asesor (físico y correo): contrato, pólizas, cuenta de cobro y carta de envío.',
  'Entrega física de documentos en el CEDI con firma en "Control Entrega Documentos".',
  'Custodia de documentación: contrato firmado por la obra entregado al área administrativa.',
  'Validación del anticipo antes de la generación del pedido.',
  'Anexo de garantía de Interdoors al contrato.'
]

export function sembrarCriterios() {
  const data = readData()
  if (data.criterios.length === 0) {
    data.criterios = TEXTO_CRITERIOS.map((texto, i) => ({ id: i + 1, texto, activo: true, orden: i }))
    writeData(data)
    return data.criterios.length
  }
  return 0
}
