// Configuración estructurada de los 25 criterios del instructivo.
// Cada criterio se descompone en sub-ítems. Un sub-ítem se cumple si:
//   (terminos vacío O coincide algún término) Y (sin patron O patron coincide) Y (sin negación O no negado)
// `minimo` = cuántos sub-ítems se requieren para marcar el criterio como "cumple".

export const CONFIG = {
  1: {
    nombre: 'Documentos del asesor comercial',
    minimo: 3,
    subItems: [
      { nombre: 'Copias físicas', terminos: ['copia fisica', 'dos copias', '2 copias', 'ejemplar', 'copia del contrato'] },
      { nombre: 'Carta de no siniestro', terminos: ['carta de no siniestro', 'no siniestro'] },
      { nombre: 'Cotización firmada y actualizada', terminos: ['cotizacion firmada', 'cotizacion actualizada', 'cotizacion firmada y actualizada'] },
      { nombre: 'Costeo detallado', terminos: ['costeo', 'costeo detallado', 'desglose de costos'] },
      { nombre: 'Manual del contratista', terminos: ['manual del contratista'] },
      { nombre: 'Documentación SST', terminos: ['sst', 'seguridad y salud en el trabajo', 'documentacion en sst', 'arl'] }
    ]
  },
  2: {
    nombre: 'Forma de pago',
    minimo: 2,
    subItems: [
      { nombre: 'Anticipo 40%', terminos: ['anticipo', 'abono inicial', 'primer pago'], patron: { tipo: 'porcentaje', valor: 40 } },
      { nombre: 'Saldo 60% contra entrega', terminos: ['saldo', 'contra entrega'], patron: { tipo: 'porcentaje', valor: 60 } },
      { nombre: 'Amortización proporcional', terminos: ['amortizacion', 'amortizado', 'amortizada'] },
      { nombre: 'Crédito 30 días', terminos: ['credito', 'plazo de credito'], patron: { tipo: 'plazo', valor: 30, unidad: 'dias' } }
    ]
  },
  3: {
    nombre: 'Independencia suministro e instalación',
    minimo: 1,
    subItems: [
      { nombre: 'Servicios independientes', terminos: ['servicios independientes', 'de manera separada', 'por separado', 'independencia', 'cobrado de manera separada'] }
    ]
  },
  4: {
    nombre: 'Facturación del suministro',
    minimo: 1,
    subItems: [
      { nombre: 'Entrega en obra', terminos: ['facturacion del suministro', 'entrega en obra', 'momento de la entrega', 'entrega del suministro'] }
    ]
  },
  5: {
    nombre: 'Facturación de la instalación',
    minimo: 1,
    subItems: [
      { nombre: 'Cortes semanales', terminos: ['facturacion de la instalacion', 'cortes semanales', 'corte semanal', 'facturacion semanal'] }
    ]
  },
  6: {
    nombre: 'Cotización',
    minimo: 2,
    subItems: [
      { nombre: 'Coincidencia precios/cantidades', terminos: ['precios y cantidades', 'coincidir en precios', 'concordancia', 'mismos precios'] },
      { nombre: 'Vigencia 30 días', terminos: ['vigencia', 'cotizacion'], patron: { tipo: 'plazo', valor: 30, unidad: 'dias' } },
      { nombre: 'Cotización presente', terminos: ['cotizacion', 'propuesta', 'oferta'] }
    ]
  },
  7: {
    nombre: 'Referencia a la cotización',
    minimo: 2,
    subItems: [
      { nombre: 'Referencia expresa', terminos: ['referencia a la cotizacion', 'hace referencia a la cotizacion', 'referencia expresa'] },
      { nombre: 'Número consecutivo', terminos: ['numero consecutivo', 'consecutivo', 'no. de cotizacion'] },
      { nombre: 'Fecha de elaboración', terminos: ['fecha de elaboracion', 'fecha de la cotizacion'] }
    ]
  },
  8: {
    nombre: 'Multas y cláusulas penales',
    minimo: 2,
    subItems: [
      { nombre: 'Cláusula penal o multa', terminos: ['clausula penal', 'multa', 'penalidad', 'sancion'] },
      { nombre: 'Bilateralidad', terminos: ['bilateral', 'mutuo acuerdo', 'equitativa', 'acuerdo entre las partes'], negacion: ['unilateral'] }
    ]
  },
  9: {
    nombre: 'Pólizas',
    minimo: 4,
    subItems: [
      { nombre: 'Póliza de cumplimiento', terminos: ['poliza de cumplimiento', 'cumplimiento'] },
      { nombre: 'Póliza de buen manejo', terminos: ['buen manejo', 'manejo de anticipo', 'poliza de anticipo'] },
      { nombre: 'Salarios y prestaciones (3 años)', terminos: ['salarios', 'prestaciones sociales', 'pago de salarios'], patron: { tipo: 'plazo', valor: 3, unidad: 'años', comparacion: '>=' } },
      { nombre: 'Calidad (12 meses)', terminos: ['calidad', 'calidad del material', 'calidad de materiales'], patron: { tipo: 'plazo', valor: 12, unidad: 'meses', comparacion: '>=' } },
      { nombre: 'Responsabilidad civil', terminos: ['responsabilidad civil'] },
      { nombre: 'Tope 100%', patron: { tipo: 'porcentaje', valor: 100 } }
    ]
  },
  10: {
    nombre: 'Ajuste de valores por demora',
    minimo: 1,
    subItems: [
      { nombre: 'Ajuste por demora', terminos: ['ajuste de valores', 'causas ajenas', 'variaciones del mercado', 'demora en la ejecucion', 'incremento'] }
    ]
  },
  11: {
    nombre: 'Documentos para liquidación de obra',
    minimo: 1,
    subItems: [
      { nombre: 'Liquidación', terminos: ['liquidacion', 'acta de liquidacion', 'documentos para la liquidacion', 'cierre del proyecto'] }
    ]
  },
  12: {
    nombre: 'Devolución del retenido',
    minimo: 1,
    subItems: [
      { nombre: 'Devolución del retenido', terminos: ['devolucion del retenido', 'liberacion', 'retenido', 'retencion'] }
    ]
  },
  13: {
    nombre: 'Reajuste por ejecución en vigencia posterior',
    minimo: 1,
    subItems: [
      { nombre: 'Reajuste', terminos: ['reajuste', 'vigencia posterior', 'ano siguiente', 'reajuste de precios'] }
    ]
  },
  14: {
    nombre: 'Términos y condiciones de garantía',
    minimo: 1,
    subItems: [
      { nombre: 'Garantía anexa', terminos: ['terminos y condiciones de la garantia', 'garantia', 'garantias y seguros', 'condiciones de la garantia'] }
    ]
  },
  15: {
    nombre: 'Revisión y aprobación del director comercial',
    minimo: 1,
    subItems: [
      { nombre: 'Director comercial', terminos: ['director comercial', 'direccion comercial', 'director de comercial'] }
    ]
  },
  16: {
    nombre: 'Requisitos para la firma de gerencia',
    minimo: 2,
    subItems: [
      { nombre: 'Dos copias', terminos: ['dos copias', '2 copias', 'dos ejemplares'] },
      { nombre: 'Firmado por director comercial', terminos: ['firmado por el director comercial', 'firma del director comercial', 'firmados por el director'] },
      { nombre: 'Cotizaciones anexas', terminos: ['cotizaciones firmadas', 'cotizaciones anexas', 'cotizaciones actualizadas'] },
      { nombre: 'Gerencia', terminos: ['gerencia', 'gerente general', 'gerente'] }
    ]
  },
  17: {
    nombre: 'Gestión documental',
    minimo: 2,
    subItems: [
      { nombre: 'Bitácora', terminos: ['bitacora'] },
      { nombre: 'Escaneado', terminos: ['escanead', 'digitalizad'] },
      { nombre: 'Nomenclatura', terminos: ['nomenclatura', 'nombre del asesor'] }
    ]
  },
  18: {
    nombre: 'Actualización de la relación de contratos',
    minimo: 2,
    subItems: [
      { nombre: 'Relación de contratos', terminos: ['relacion de contratos'] },
      { nombre: 'Días 15 y 30', terminos: ['dias 15 y 30', '15 y 30'] },
      { nombre: 'Firma del gerente', terminos: ['firma del gerente', 'gerente general'] }
    ]
  },
  19: {
    nombre: 'Solicitud de anticipo y pólizas',
    minimo: 2,
    subItems: [
      { nombre: 'Analista de cartera', terminos: ['analista de cartera'] },
      { nombre: 'Jefe administrativo', terminos: ['jefe administrativo', 'jefe administrativa', 'jefatura administrativa'] },
      { nombre: 'Cuenta de cobro', terminos: ['cuenta de cobro'] },
      { nombre: 'Correo electrónico', terminos: ['correo electronico', 'correo', 'email', 'e-mail'] }
    ]
  },
  20: {
    nombre: 'Firma y gestión de pólizas',
    minimo: 1,
    subItems: [
      { nombre: 'Firma de pólizas', terminos: ['firma de las polizas', 'firma de polizas', 'polizas firmadas', 'firmar las polizas'] }
    ]
  },
  21: {
    nombre: 'Entrega de documentos al asesor',
    minimo: 2,
    subItems: [
      { nombre: 'Contrato u otrosí firmado', terminos: ['contrato firmado', 'otrosi firmado', 'otrosi'] },
      { nombre: 'Pólizas firmadas', terminos: ['polizas firmadas'] },
      { nombre: 'Cuenta de cobro del anticipo', terminos: ['cuenta de cobro', 'cuenta de cobro del anticipo'] },
      { nombre: 'Carta de envío', terminos: ['carta de envio'] },
      { nombre: 'Correo electrónico', terminos: ['correo electronico', 'correo'] }
    ]
  },
  22: {
    nombre: 'Entrega física de documentos (CEDI)',
    minimo: 1,
    subItems: [
      { nombre: 'CEDI', terminos: ['cedi', 'control entrega documentos', 'asistente de despacho', 'jefe de cedi'] }
    ]
  },
  23: {
    nombre: 'Custodia de documentación',
    minimo: 1,
    subItems: [
      { nombre: 'Custodia', terminos: ['custodia', 'area administrativa', 'custodia de documentacion', 'archivo de documentacion'] }
    ]
  },
  24: {
    nombre: 'Validación de anticipo y generación de pedido',
    minimo: 2,
    subItems: [
      { nombre: 'Anticipo pagado', terminos: ['anticipo pagado', 'anticipo abonado', 'confirmacion del anticipo', 'abono correspondiente'] },
      { nombre: 'Generación de pedido', terminos: ['generacion de pedido', 'generar pedido', 'pedido'] },
      { nombre: 'Fabricación condicionada', terminos: ['enviarse a fabricar', 'inicio de fabricacion', 'proceso de fabricacion'] }
    ]
  },
  25: {
    nombre: 'Anexo de garantía de Interdoors',
    minimo: 1,
    subItems: [
      { nombre: 'Anexo de garantía', terminos: ['anexo de garantia', 'garantia de interdoors', 'garantia interdoors'] }
    ]
  }
}
