# Base de conocimiento: Lista de chequeo de gestión de contratos

**Fuente:** Instructivo de la Lista de Chequeo de Gestión de Contratos
2025 (V11092025), Interdoors.\
**Versión de esta base:** 1.0\
**Propósito:** permitir que un sistema automatizado identifique en
contratos y documentos relacionados los requisitos del instructivo
aunque estén redactados con palabras distintas, sin exigir coincidencias
literales.

------------------------------------------------------------------------

## 1. Instrucciones generales para el motor de reconocimiento

### 1.1 Principio de interpretación

Identificar el **significado y las condiciones del requisito**, no
solamente la coincidencia exacta de palabras. Una expresión puede
considerarse equivalente si conserva el mismo sentido contractual.

Ejemplos: - `40%` puede aparecer como `cuarenta por ciento` o
`0,40 del valor total`. - `30 días calendario` puede aparecer como
`un mes`, siempre que el contexto permita concluir que se refiere a la
vigencia de la cotización. La equivalencia temporal debe marcarse para
revisión si no es inequívoca. - `contra entrega` puede aparecer como
`una vez recibidos los productos` o `al momento de la entrega en obra`.

### 1.2 Estados que debe devolver el sistema

Cada criterio debe recibir uno de estos estados:

-   **CUMPLE:** se encontró evidencia suficiente y coherente con todas
    las condiciones esenciales del criterio.
-   **NO CUMPLE:** se encontró evidencia expresa que contradice una
    condición esencial.
-   **PARCIAL:** se encontró parte del requisito, pero falta otra
    condición necesaria.
-   **NO IDENTIFICADO:** no se encontró evidencia suficiente en los
    documentos analizados. No equivale automáticamente a incumplimiento.
-   **NO APLICA:** el criterio depende de una condición que no se
    presenta en el caso (por ejemplo, una exigencia específica para
    constructoras), y esa no aplicabilidad está sustentada.
-   **REVISIÓN HUMANA:** hay ambigüedad, contradicción, excepción o
    equivalencia dudosa que no debe resolver automáticamente el sistema.

### 1.3 Reglas obligatorias

1.  No exigir que el contrato copie literalmente el instructivo.
2.  Aceptar sinónimos, paráfrasis, abreviaturas y números escritos en
    letras o cifras.
3.  Analizar el contexto de la frase y el documento; no validar por una
    palabra aislada.
4.  No declarar **CUMPLE** por encontrar solamente una palabra clave.
    Deben estar presentes las condiciones esenciales.
5.  No asumir que un requisito está incluido porque sea una práctica
    habitual o porque aparezca en otro contrato.
6.  Distinguir entre ausencia de evidencia y evidencia de
    incumplimiento.
7.  Si dos documentos se contradicen (por ejemplo, contrato y
    cotización), marcar **REVISIÓN HUMANA** o **NO CUMPLE**, según la
    regla específica; nunca ocultar la contradicción.
8.  Conservar un fragmento textual de evidencia, nombre del archivo y
    página o ubicación cuando sea posible.
9.  Los requisitos condicionales deben evaluarse según su condición de
    aplicabilidad. Si no se conoce si la condición aplica, usar
    **REVISIÓN HUMANA**.
10. Las excepciones mencionadas en el instructivo requieren validación
    por el responsable indicado; el sistema no debe aprobarlas por sí
    solo.

### 1.4 Datos que debe producir el script por cada criterio

``` json
{
  "criterio_id": "GC-02",
  "criterio": "Forma de pago",
  "estado": "PARCIAL",
  "confianza": 0.87,
  "evidencia": [
    {
      "texto": "El contratante pagará un anticipo equivalente al 40% del contrato.",
      "documento": "Contrato.pdf",
      "pagina": 3
    }
  ],
  "condiciones_verificadas": {
    "anticipo_40_por_ciento": true,
    "saldo_60_por_ciento_contra_entrega": false,
    "amortizacion_proporcional_si_hay_cortes_parciales": null,
    "credito_30_dias_sujeto_a_requisitos": null
  },
  "observacion": "Se identificó el anticipo, pero no se encontró la condición del saldo contra entrega."
}
```

La confianza es una estimación del motor de búsqueda o similitud, no una
prueba de cumplimiento. El estado debe depender también de la validación
de las condiciones.

### 1.5 Normalización recomendada

Antes de comparar textos: - Convertir a minúsculas y normalizar tildes
para la búsqueda, conservando el texto original para la evidencia. -
Unificar espacios, saltos de línea y guiones. - Reconocer porcentajes en
cifras y letras. - Reconocer variantes como `N.º`, `No.`, `número` y
`consecutivo`. - Reconocer unidades temporales: días calendario, días
naturales, meses y años. No convertirlas automáticamente si la
equivalencia puede cambiar el requisito. - Mantener negaciones y
restricciones: `no`, `excepto`, `únicamente`, `solo`, `siempre que`,
`salvo`, `previa aprobación`. - Detectar quién asume la obligación:
contratante, contratista, cliente, proveedor, Interdoors u obra. No
asumir que son intercambiables si cambia el responsable.

------------------------------------------------------------------------

# 2. Criterios reconocibles

## GC-01. Documentos que debe enviar el asesor comercial

**Requisito fuente:** el asesor debe reunir y entregar los documentos
requeridos: dos copias físicas del contrato; cuando se trate de
constructoras, carta de no siniestro; cotización firmada y actualizada
con costeo detallado; manual del contratista; documentación de SST y
otros documentos requeridos, firmados por el coordinador de SST cuando
aplique.

**Objetivo de reconocimiento:** identificar la relación de documentos
que acompaña el contrato y verificar que estén contemplados o
disponibles.

**Conceptos y expresiones relacionadas:** - documentos para formalizar
el contrato - documentación contractual / soportes del contrato -
ejemplares / copias originales / dos tantos - cotización comercial /
oferta económica / propuesta - cotización suscrita, aprobada o firmada -
análisis de costos / desglose de costos / costeo - manual de
contratistas / manual del contratista - SST / seguridad y salud en el
trabajo / seguridad industrial y salud ocupacional - carta de no
siniestro / certificación de no reclamaciones o siniestros

**Condiciones de validación:** - Identificar la exigencia o presencia de
dos copias físicas del contrato. - Identificar cotización firmada y
vigente/actualizada. - Identificar costeo o desglose detallado. -
Identificar manual del contratista. - Identificar documentación de
SST. - Identificar otros anexos requeridos y firma del coordinador SST
cuando corresponda. - La carta de no siniestro es condicional para
constructoras.

**Reglas de decisión:** - Si el documento solo menciona "anexos" sin
enumerarlos, no marcar CUMPLE: usar NO IDENTIFICADO o REVISIÓN HUMANA. -
Si el contrato indica que se adjunta una cotización, pero no se dispone
de ella, reportar evidencia parcial y solicitar el archivo. - Si se
confirma que el cliente no es una constructora, la carta de no siniestro
puede marcarse NO APLICA, dejando constancia de la condición.

**Búsqueda semántica sugerida:**
`documentos requeridos para suscribir el contrato`,
`anexos contractuales`, `copias del contrato`, `cotización firmada`,
`costos detallados`, `manual del contratista`,
`documentos de seguridad y salud en el trabajo`.

## GC-02. Forma de pago

**Requisito fuente:** anticipo del 40% del valor total; saldo del 60%
facturado contra entrega del suministro; si hay facturaciones parciales,
amortización proporcional del anticipo; crédito de 30 días calendario
únicamente para clientes que cumplan los requisitos del área encargada.

**Conceptos y expresiones relacionadas:** - anticipo / pago inicial /
abono inicial / desembolso inicial - cuarenta por ciento / 40% / 0,40 -
valor total / valor global / monto total del contrato - saldo /
remanente / valor restante / 60% / sesenta por ciento - contra entrega /
al entregar / una vez recibido el suministro - amortizar / descontar /
aplicar proporcionalmente el anticipo - cortes / entregas / facturas
parciales - crédito a 30 días / plazo de pago de treinta días
calendario - aprobación de crédito / cupo autorizado / requisitos de
cartera

**Condiciones de validación:** - Anticipo equivalente al 40% del valor
total. - Saldo del 60% facturado contra entrega del suministro. - Si se
contemplan facturaciones parciales, debe establecerse la amortización
proporcional del anticipo. - El crédito de 30 días solo puede
considerarse dentro de las condiciones autorizadas por el área
encargada.

**Reglas de decisión:** - Comparar porcentajes contra el valor total del
contrato, no contra una base distinta. - Si los porcentajes no suman
100% o difieren de 40/60, marcar NO CUMPLE o REVISIÓN HUMANA si hay una
excepción documentada. - No exigir una cláusula de amortización si no
existen facturaciones parciales; si el contrato sí prevé cortes
parciales y no indica cómo amortizar, marcar PARCIAL. - La mención de
crédito no significa que esté aprobado: verificar la condición de
autorización. - Una forma de pago distinta requiere validación humana;
no asumir que es aceptable.

**Búsqueda semántica sugerida:** `condiciones económicas`,
`esquema de pagos`, `porcentaje inicial`, `pago del remanente`,
`amortización del anticipo`, `crédito comercial`, `plazo de pago`.

## GC-03. Independencia de suministro e instalación

**Requisito fuente:** suministro e instalación son servicios
independientes. El cobro del suministro no debe quedar condicionado a la
ejecución de la instalación; cada concepto se factura y cobra
separadamente, según corresponda.

**Conceptos y expresiones relacionadas:** - suministro / entrega de
productos / provisión de bienes - instalación / montaje / puesta en
obra - servicios independientes / conceptos separados / actividades
diferenciadas - facturación separada / cobro independiente - no
condicionado / no supeditado / sin depender de - pago del suministro
aunque la instalación esté pendiente

**Condiciones de validación:** - El contrato debe permitir distinguir
suministro e instalación como conceptos o servicios independientes. - El
pago o cobro del suministro no debe depender de que se haya ejecutado la
instalación. - La facturación y el cobro deben poder realizarse por
separado cuando corresponda.

**Reglas de decisión:** - Si el contrato condiciona el pago total del
suministro a la instalación completa, marcar NO CUMPLE. - Si diferencia
los valores pero no aclara la independencia de cobro, marcar PARCIAL o
REVISIÓN HUMANA. - No interpretar la sola aparición de las palabras
"suministro" e "instalación" como cumplimiento.

**Búsqueda semántica sugerida:**
`suministro e instalación por separado`, `servicios autónomos`,
`cobro independiente`, `facturación independiente`,
`no depende de la instalación`.

## GC-04. Facturación del suministro

**Requisito fuente:** la facturación del suministro se realiza al
momento de la entrega en obra, parcial o por el total del pedido, de
acuerdo con lo previamente acordado con la obra.

**Conceptos y expresiones relacionadas:** - facturar / emitir factura /
radicar factura / cobrar - suministro / productos / materiales /
elementos entregados - entrega en obra / recepción en el proyecto /
recibido en sitio - entrega parcial / despachos parciales / entregas por
lotes - pedido completo / totalidad del pedido - según lo acordado /
conforme al cronograma pactado

**Condiciones de validación:** - La facturación debe estar vinculada al
momento de entrega del suministro en obra. - Debe contemplarse entrega
parcial o total de acuerdo con lo acordado.

**Reglas de decisión:** - Si la factura se condiciona exclusivamente a
la instalación, marcar NO CUMPLE y relacionar también GC-03. - Si se
establece un hito de facturación diferente, marcar REVISIÓN HUMANA. - No
confundir fecha de despacho con entrega/recepción en obra si el contrato
las diferencia.

**Búsqueda semántica sugerida:** `facturación al entregar`,
`factura por despacho recibido`, `entregas parciales`,
`recibo de materiales en obra`.

## GC-05. Facturación de la instalación

**Requisito fuente:** la instalación se factura mediante cortes
semanales, con base en la entrega efectuada en obra; la obra debe
garantizar disponibilidad de recepción para permitir la ejecución y
facturación del servicio.

**Conceptos y expresiones relacionadas:** - instalación / montaje / mano
de obra de instalación - corte semanal / acta semanal / medición semanal
/ avance semanal - facturación periódica / cobro por avances - entrega
efectuada / actividades ejecutadas / avance realizado - disponibilidad
de recepción / personal para recibir / acceso y recepción en obra

**Condiciones de validación:** - La facturación de instalación debe
contemplar cortes semanales. - Los cortes deben basarse en la entrega o
avance efectivamente realizado en obra. - Debe reconocerse la
disponibilidad de recepción por parte de la obra.

**Reglas de decisión:** - Si el contrato prevé únicamente facturación al
finalizar toda la instalación, marcar NO CUMPLE o REVISIÓN HUMANA según
la redacción. - Si hay cortes semanales, pero no se define su base,
marcar PARCIAL. - No confundir los cortes de instalación con las
entregas del suministro.

**Búsqueda semántica sugerida:** `actas semanales de instalación`,
`cortes de obra`, `cobro semanal por avance`, `recepción de trabajos`.

## GC-06. Cotización

**Requisito fuente:** la cotización debe coincidir en precios y
cantidades con el contrato; su vigencia es de 30 días calendario desde
la emisión; antes de formalizar el contrato se verifican los precios.

**Conceptos y expresiones relacionadas:** - cotización / oferta /
propuesta económica / presupuesto comercial - precios / valores
unitarios / tarifas / valor ofertado - cantidades / unidades / número de
elementos - vigencia / validez / plazo de aceptación - treinta días
calendario / 30 días naturales - fecha de emisión / fecha de
expedición - actualización / revisión de precios / validación comercial

**Condiciones de validación:** - Debe existir correspondencia entre
precios de cotización y contrato. - Debe existir correspondencia entre
cantidades de cotización y contrato. - La cotización debe tener vigencia
de 30 días calendario contados desde su emisión. - Debe existir
verificación de precios antes de formalizar.

**Reglas de decisión:** - Comparar valores y cantidades cuando ambos
documentos estén disponibles; no basta con que el contrato diga que "se
acepta la cotización". - Si la cotización está vencida al formalizarse,
marcar NO CUMPLE o REVISIÓN HUMANA si existe aprobación/actualización
documentada. - Si falta la cotización, marcar NO IDENTIFICADO y
solicitarla. - No asumir que "un mes" equivale siempre a 30 días
calendario sin comprobar el contexto y las fechas.

**Búsqueda semántica sugerida:** `oferta económica vigente`,
`precios y cantidades ofertados`, `validez de la propuesta`,
`revisión de valores antes de suscribir`.

## GC-07. Referencia a la cotización

**Requisito fuente:** el contrato debe mencionar expresamente el número
consecutivo y la fecha de elaboración de la cotización. Esa referencia
también debe aparecer en documentos asociados, como pólizas y cuentas de
cobro. La verificación corresponde al analista de cartera y al jefe
administrativo.

**Conceptos y expresiones relacionadas:** - cotización / oferta
comercial / propuesta económica - número consecutivo / número de
cotización / código / referencia - fecha de elaboración / fecha de
emisión / expedición - póliza / garantía / cuenta de cobro - documentos
asociados / soportes relacionados

**Condiciones de validación:** - El contrato identifica la cotización
por número o código. - El contrato indica la fecha de
elaboración/emisión. - La referencia debe coincidir en pólizas y cuentas
de cobro cuando esos documentos estén disponibles.

**Reglas de decisión:** - Si aparece el número pero no la fecha, marcar
PARCIAL. - Si el contrato remite genéricamente a "la cotización anexa"
sin identificarla, marcar PARCIAL. - Si los consecutivos o fechas
difieren entre documentos, marcar REVISIÓN HUMANA y mostrar ambas
evidencias. - La verificación de documentos asociados puede quedar
pendiente si todavía no se han emitido.

**Búsqueda semántica sugerida:** `cotización número`,
`propuesta identificada con`, `consecutivo y fecha`,
`referencia de oferta en pólizas`.

## GC-08. Multas y cláusulas penales

**Requisito fuente:** no se aceptan multas ni cláusulas penales
unilaterales. Si las partes acuerdan incluirlas, deben establecerse
bilateralmente y en condiciones equitativas.

**Conceptos y expresiones relacionadas:** - multa / sanción económica /
penalidad - cláusula penal / pena convencional / indemnización pactada -
unilateral / a cargo exclusivo de una parte - bilateral / recíproca /
para ambas partes - contratante y contratista / ambas partes -
condiciones equitativas / proporcionales / simétricas

**Condiciones de validación:** - Detectar si existen multas o cláusulas
penales. - Si existen, verificar que puedan aplicarse bilateralmente y
no solo contra el contratista. - Revisar si las obligaciones y
consecuencias se expresan de manera recíproca.

**Reglas de decisión:** - Una penalidad aplicable únicamente al
contratista se considera NO CUMPLE. - Si no existen multas ni cláusulas
penales, el criterio puede considerarse CUMPLE respecto de la
prohibición de unilateralidad, dejando evidencia de la búsqueda. - Si
hay una cláusula aparentemente bilateral pero con obligaciones o
consecuencias asimétricas, marcar REVISIÓN HUMANA. - No concluir
bilateralidad solo porque el texto diga "las partes"; revisar quién
puede ser sancionado.

**Búsqueda semántica sugerida:** `cláusula penal`,
`multa por incumplimiento`, `sanción a cargo del contratista`,
`penalidad recíproca`, `responsabilidad de ambas partes`.

## GC-09. Pólizas

**Requisito fuente:** presentar las pólizas exigidas según corresponda y
verificar vigencias y condiciones. Se enumeran: cumplimiento, buen
manejo, pago de salarios y prestaciones sociales (vigencia mínima de 3
años), calidad (vigencia mínima de 12 meses) y responsabilidad civil. La
suma porcentual total de las pólizas no puede superar el 100% del valor
del contrato. Las excepciones deben validarse con jefe administrativo o
director comercial.

**Conceptos y expresiones relacionadas:** - póliza / garantía / amparo /
seguro - cumplimiento / cumplimiento contractual - buen manejo /
correcta inversión / manejo del anticipo - salarios / prestaciones
sociales / obligaciones laborales - calidad / estabilidad o calidad de
los bienes, según la denominación usada - responsabilidad civil /
responsabilidad civil extracontractual - vigencia / duración / cobertura
/ fecha de expiración - suma asegurada / valor asegurado / porcentaje
amparado - aseguradora / compañía de seguros

**Condiciones de validación:** - Identificar cuáles pólizas exige el
contrato y cuáles son aplicables al caso. - Verificar la presencia o
exigencia de los amparos enumerados según corresponda. - Amparo de
salarios y prestaciones: vigencia mínima de 3 años. - Amparo de calidad:
vigencia mínima de 12 meses. - La suma porcentual total de pólizas no
debe superar el 100% del valor contractual. - Registrar excepciones y
evidencia de validación por jefe administrativo o director comercial.

**Reglas de decisión:** - No asumir que todas las pólizas aplican
automáticamente en todos los contratos: el instructivo dice "según
corresponda". - No confundir valor asegurado individual con suma
porcentual total. Calcular el total solo si las bases porcentuales son
comparables. - Si no se dispone de las pólizas, el contrato puede
identificar la obligación, pero la verificación de vigencias queda
pendiente. - Vigencias inferiores a los mínimos indicados deben marcar
NO CUMPLE, salvo excepción aprobada documentadamente. - Una excepción no
documentada debe quedar en REVISIÓN HUMANA.

**Búsqueda semántica sugerida:** `garantías contractuales`,
`amparo de cumplimiento`, `buen manejo del anticipo`,
`salarios y prestaciones`, `calidad`, `responsabilidad civil`,
`vigencia de amparos`, `valor asegurado`.

## GC-10. Ajuste de valores por demora en la ejecución

**Requisito fuente:** si la ejecución supera la fecha pactada por causas
ajenas a INTERDOORS, los valores de suministro y/o instalación pueden
estar sujetos a incrementos por variaciones del mercado. Se debe validar
con el jefe administrativo el anexo solicitado al área jurídica para
complementar la cláusula.

**Conceptos y expresiones relacionadas:** - demora / retraso / prórroga
/ extensión del plazo - causas ajenas a INTERDOORS / no imputables a
INTERDOORS - variaciones del mercado / inflación / incremento de
costos - reajuste / actualización / incremento de precios / revisión de
valores - suministro y/o instalación - anexo jurídico / documento
complementario / otrosí

**Condiciones de validación:** - Debe contemplarse la posibilidad de
ajustar valores si la ejecución se retrasa por causas ajenas a
INTERDOORS y supera la fecha pactada. - El ajuste debe relacionarse con
variaciones del mercado. - Debe verificarse el anexo complementario
indicado por el instructivo con el jefe administrativo.

**Reglas de decisión:** - Una cláusula general de reajuste sin relación
con demoras ajenas a INTERDOORS puede ser solo coincidencia parcial. -
Si el contrato congela expresamente los precios sin posibilidad de
ajuste en ese supuesto, marcar NO CUMPLE o REVISIÓN HUMANA. - La
presencia de la cláusula no demuestra que el anexo jurídico haya sido
validado; registrar esa tarea por separado.

**Búsqueda semántica sugerida:** `reajuste por retrasos`,
`prórroga no imputable al contratista`,
`variación de precios por extensión del plazo`,
`mayores costos de mercado`.

## GC-11. Documentos para la liquidación de la obra

**Requisito fuente:** el contrato debe indicar expresamente los
documentos requeridos para liquidar la obra y debe confirmarse su
cumplimiento. Si alguno no está estipulado, debe solicitarse al
contratante antes del cierre. La validación y firma corresponde al
director comercial o gerente general.

**Conceptos y expresiones relacionadas:** - liquidación / cierre
contractual / acta de liquidación / cierre de obra - documentos soporte
/ requisitos de cierre / paz y salvo / actas / certificaciones - entrega
de documentos / presentación de soportes - contratante / cliente /
constructor

**Condiciones de validación:** - Identificar una relación expresa de
documentos o requisitos para liquidar/cerrar la obra. - Verificar que se
haya confirmado o gestionado su entrega. - Si falta algún requisito en
el contrato, debe solicitarse al contratante antes del cierre. -
Identificar validación/firma del director comercial o gerente general.

**Reglas de decisión:** - Una referencia genérica a "cumplir los
requisitos de liquidación" sin enumerarlos es PARCIAL. - No inventar
cuáles documentos son necesarios: el instructivo no proporciona una
lista cerrada. - Si aún no ha llegado la etapa de cierre, separar la
revisión de la cláusula contractual de la verificación de entrega
efectiva.

**Búsqueda semántica sugerida:** `requisitos para liquidar`,
`documentación de cierre`, `acta de liquidación`,
`soportes para cierre de obra`.

## GC-12. Devolución del retenido

**Requisito fuente:** el contrato debe expresar los requisitos para
devolver el retenido, especificando documentos, plazos y condiciones
para su liberación.

**Conceptos y expresiones relacionadas:** - retenido / retención / suma
retenida / fondo de garantía - devolución / liberación / reintegro /
pago del retenido - documentos para liberar / soportes requeridos -
plazo / término / fecha / condición de liberación - recibo final / acta
de entrega / liquidación (solo como posibles expresiones contextuales)

**Condiciones de validación:** - Debe identificarse qué activa la
devolución o liberación. - Deben identificarse documentos requeridos. -
Debe existir un plazo o término. - Deben quedar claras las condiciones
de liberación.

**Reglas de decisión:** - Si solo se menciona un porcentaje retenido,
pero no cómo ni cuándo se devuelve, marcar PARCIAL. - Si no existe
retención en el contrato, marcar NO APLICA únicamente cuando esa
ausencia esté confirmada. - No inventar plazos ni documentos que el
instructivo no especifica.

**Búsqueda semántica sugerida:** `retención en garantía`,
`liberación de valores retenidos`, `devolución del retenido`,
`requisitos de reintegro`.

## GC-13. Reajuste por ejecución en vigencia posterior

**Requisito fuente:** si suministro y/o instalación se ejecutan en el
año siguiente al de la cotización, se debe solicitar reajuste de precios
conforme al mercado o, en su defecto, obtener aprobación expresa de
Dirección Comercial.

**Conceptos y expresiones relacionadas:** - año siguiente / vigencia
posterior / siguiente periodo anual - ejecución posterior a la
cotización / entrega en año posterior - reajuste / actualización /
revisión de precios - variación del mercado / nuevos precios /
incremento de costos - aprobación expresa / autorización escrita / visto
bueno formal - Dirección Comercial / director comercial

**Condiciones de validación:** - Detectar si la ejecución se realizará
en un año calendario posterior al de la cotización. - Si ocurre, debe
existir solicitud o previsión de reajuste conforme al mercado, o
aprobación expresa de Dirección Comercial para no reajustar.

**Reglas de decisión:** - Este criterio es condicional: si no hay
ejecución en año posterior, puede marcarse NO APLICA con sustento. - Una
aprobación verbal o no identificable no debe considerarse aprobación
expresa. - No confundir una prórroga dentro del mismo año con ejecución
en el año siguiente.

**Búsqueda semántica sugerida:** `precios para la siguiente vigencia`,
`reajuste anual`, `ejecución en año posterior`,
`aprobación de precios por Dirección Comercial`.

## GC-14. Términos y condiciones de garantía

**Requisito fuente:** anexar al contrato los términos y condiciones de
garantía aplicables a los productos suministrados, específicamente
puertas y muebles, indicando alcance, vigencia y procedimiento de
reclamación.

**Conceptos y expresiones relacionadas:** - garantía / respaldo /
cobertura / garantía de producto - puertas / muebles / carpintería /
productos suministrados - anexo / documento adjunto / condiciones de
garantía - alcance / cobertura / exclusiones - vigencia / duración /
periodo de garantía - reclamación / solicitud de garantía / trámite por
defectos

**Condiciones de validación:** - Debe identificarse el documento o
cláusula de garantía aplicable a los productos. - Debe especificar
alcance o cobertura. - Debe especificar vigencia. - Debe explicar el
procedimiento para reclamar.

**Reglas de decisión:** - La frase "se garantiza la calidad" por sí sola
no demuestra que estén definidos alcance, vigencia y procedimiento. - Si
el contrato remite a un anexo que no está entre los archivos analizados,
marcar PARCIAL y solicitar el anexo. - No inventar periodos de garantía:
el instructivo no fija una duración general en este criterio.

**Búsqueda semántica sugerida:** `garantía de puertas y muebles`,
`condiciones de garantía anexas`, `cobertura y vigencia`,
`procedimiento para hacer efectiva la garantía`.

## GC-15. Revisión y aprobación del contrato

**Requisito fuente:** el director comercial debe revisar previamente y
firmar el contrato como constancia de validación; luego se remite a
Gerencia para aprobación final.

**Conceptos y expresiones relacionadas:** - revisión comercial / visto
bueno / validación previa - director comercial / dirección comercial -
firma / suscripción / aprobación - remisión a gerencia / envío a
gerencia general - aprobación final / autorización de gerencia

**Condiciones de validación:** - Debe existir revisión previa del
director comercial. - Debe constar su firma. - Después, el contrato debe
remitirse a Gerencia para aprobación final.

**Reglas de decisión:** - Una firma de gerencia sin evidencia de
revisión/firma previa del director comercial no acredita por sí sola
todo el flujo. - Distinguir firma del director comercial de la firma del
gerente general. - Si solo se dispone de un borrador, marcar NO
IDENTIFICADO para las firmas.

**Búsqueda semántica sugerida:** `revisado por Dirección Comercial`,
`firma del director comercial`, `aprobación de gerencia`,
`visto bueno comercial`.

## GC-16. Requisitos para la firma de gerencia

**Requisito fuente:** para solicitar la firma de Gerencia se deben
presentar dos copias de los documentos del contrato, previamente
firmadas por el director comercial, y anexar las cotizaciones firmadas y
actualizadas.

**Conceptos y expresiones relacionadas:** - firma de gerencia / firma
del gerente general - dos copias / dos ejemplares / dos tantos -
documentos contractuales - firma previa del director comercial -
cotización firmada / propuesta suscrita - cotización actualizada /
vigente

**Condiciones de validación:** - Dos copias de los documentos del
contrato. - Firma previa del director comercial. - Cotizaciones
correspondientes firmadas y actualizadas.

**Reglas de decisión:** - No confundir este requisito operativo de
presentación con la aprobación final del criterio GC-15. - Si se indica
que el contrato está firmado por gerencia, pero no hay evidencia de los
dos ejemplares o de las cotizaciones, marcar PARCIAL. - Si las
cotizaciones no están disponibles, dejar pendiente su verificación.

**Búsqueda semántica sugerida:** `documentos para firma del gerente`,
`dos ejemplares firmados`, `cotización actualizada anexa`,
`firma previa de Dirección Comercial`.

## GC-17. Gestión documental

**Requisito fuente:** una vez firmados los documentos, deben escanearse
y guardarse en la bitácora siguiendo la nomenclatura: nombre del asesor,
nombre de la constructora y nombre de la obra.

**Conceptos y expresiones relacionadas:** - escanear / digitalizar /
convertir a PDF - guardar / archivar / cargar / subir - carpeta Bitácora
/ repositorio del proyecto - nombre del asesor / responsable comercial -
constructora / cliente constructor - obra / proyecto

**Condiciones de validación:** - Los documentos firmados deben
digitalizarse. - Deben guardarse en la carpeta o sección Bitácora. - La
identificación o nomenclatura debe incluir asesor, constructora y obra.

**Reglas de decisión:** - La cláusula del contrato no suele demostrar
que el archivo haya sido guardado: este criterio requiere revisar el
repositorio o evidencia documental. - Si solo se encuentra el archivo
pero no puede verificarse su ubicación o nomenclatura, marcar PARCIAL. -
No declarar CUMPLE basándose únicamente en que el contrato ordena
archivar.

**Búsqueda semántica sugerida:** `archivo digital del contrato`,
`documentos escaneados`, `carpeta de bitácora`,
`identificación por asesor, constructora y obra`.

## GC-18. Actualización de la relación de contratos

**Requisito fuente:** en la carpeta Bitácora debe actualizarse el
documento "Relación de Contratos" con los datos del nuevo contrato. Para
otrosí por prórroga se modifica el tiempo. Debe mantenerse actualizado
los días 15 y 30 de cada mes, registrar la fecha de inicio del trámite y
contar con firma del gerente general.

**Conceptos y expresiones relacionadas:** - relación de contratos /
registro maestro / listado de contratos - actualizar / registrar /
incorporar / diligenciar - otrosí / adenda / modificación contractual -
prórroga / ampliación de plazo / extensión del término - fecha de inicio
del trámite / radicación / apertura de gestión - firma del gerente
general - actualización quincenal / días 15 y 30

**Condiciones de validación:** - El nuevo contrato debe registrarse en
la Relación de Contratos. - Si es un otrosí por prórroga, debe
actualizarse el plazo o duración. - Registrar fecha de inicio del
trámite. - Contar con firma del gerente general. - Mantener
actualización los días 15 y 30 de cada mes.

**Reglas de decisión:** - Requiere inspección del archivo "Relación de
Contratos" o evidencia de su actualización; el contrato por sí solo no
prueba el registro. - Si el documento no está disponible, marcar NO
IDENTIFICADO. - No interpretar que cualquier otrosí implica prórroga:
comprobar el tipo de modificación.

**Búsqueda semántica sugerida:** `registro de contratos`,
`matriz de contratos`, `actualización del listado`,
`otrosí de ampliación de plazo`, `fecha de inicio del trámite`.

## GC-19. Solicitud de anticipo y pólizas

**Requisito fuente:** enviar correo al analista de cartera y al jefe
administrativo solicitando la cuenta de cobro del anticipo y las pólizas
requeridas. Si la constructora indica aseguradoras expresamente en el
contrato, especificarlas en la solicitud. Archivar la documentación en
Bitácora junto con el contrato.

**Conceptos y expresiones relacionadas:** - correo / email /
comunicación / solicitud formal - analista de cartera / área de
cartera - jefe administrativo / administración - cuenta de cobro /
documento de cobro del anticipo - expedición / emisión de pólizas -
aseguradora / compañía aseguradora - archivo en Bitácora

**Condiciones de validación:** - Evidencia de correo enviado a analista
de cartera y jefe administrativo. - Solicitud de cuenta de cobro del
anticipo. - Solicitud de pólizas requeridas. - Si el contrato determina
aseguradoras específicas, estas deben mencionarse en la solicitud. -
Archivar la documentación en Bitácora junto con el contrato.

**Reglas de decisión:** - La obligación escrita en el contrato no prueba
que el correo haya sido enviado. - Si no se dispone del correo, marcar
NO IDENTIFICADO para la gestión. - La mención de aseguradora específica
es condicional a que la constructora la haya indicado expresamente.

**Búsqueda semántica sugerida:** `solicitud de cuenta de cobro`,
`correo para expedición de pólizas`,
`aseguradora definida por la constructora`,
`archivo de soportes en bitácora`.

## GC-20. Firma y gestión de pólizas

**Requisito fuente:** solicitar a Gerencia la firma de las pólizas. Una
vez firmadas, escanearlas y archivarlas en Bitácora con nomenclatura de
asesor, constructora, obra, contrato y pólizas.

**Conceptos y expresiones relacionadas:** - pólizas firmadas / garantías
suscritas - solicitud de firma a gerencia / gerente general - escanear /
digitalizar - archivar / cargar / guardar - Bitácora - asesor /
constructora / obra / contrato / pólizas

**Condiciones de validación:** - Solicitud de firma de las pólizas a
Gerencia. - Evidencia de pólizas firmadas. - Digitalización de las
pólizas firmadas. - Archivo en Bitácora. - Nomenclatura que identifique
asesor, constructora, obra, contrato y pólizas.

**Reglas de decisión:** - No confundir la existencia de una póliza
emitida con una póliza firmada por Gerencia. - Si las pólizas todavía no
se han emitido, registrar pendiente/no identificado, según la etapa. -
La evidencia de archivo debe provenir del repositorio o de un registro
verificable, no solo de una cláusula contractual.

**Búsqueda semántica sugerida:** `firma de garantías por gerencia`,
`pólizas suscritas`, `pólizas digitalizadas`,
`archivo de pólizas en bitácora`.

## GC-21. Entrega de documentos al asesor

**Requisito fuente:** enviar al asesor en formato físico y por correo
electrónico: contrato u otrosí firmado (dos ejemplares), pólizas
firmadas (para contrato u otrosí), cuenta de cobro del anticipo y carta
de envío de documentos.

**Conceptos y expresiones relacionadas:** - entrega / remisión / envío /
devolución al asesor - físico y digital / correo electrónico - contrato
firmado / otrosí firmado / modificación suscrita - dos ejemplares / dos
copias - pólizas firmadas - cuenta de cobro del anticipo - carta
remisoria / carta de envío / relación de documentos entregados

**Condiciones de validación:** - Entrega física y envío por correo
electrónico. - Contrato u otrosí firmado en dos ejemplares. - Pólizas
firmadas, cuando correspondan. - Cuenta de cobro del anticipo. - Carta
de envío de documentos.

**Reglas de decisión:** - Verificar tanto el canal físico como el
electrónico; uno no sustituye automáticamente al otro. - Las pólizas
aplican para contrato y otrosí según corresponda. - Si falta un soporte
de entrega, marcar PARCIAL. - No considerar que adjuntar un documento en
un correo equivale a entrega física.

**Búsqueda semántica sugerida:** `remisión de documentos al asesor`,
`entrega de contrato y pólizas`, `dos ejemplares`,
`correo con soportes`, `carta remisoria`.

## GC-22. Entrega física de documentos

**Requisito fuente:** la documentación física debe entregarse en el
CEDI. El asistente de despacho o jefe de CEDI debe firmar el documento
"Control Entrega Documentos" como constancia de recepción.

**Conceptos y expresiones relacionadas:** - CEDI / centro de
distribución - entrega física / radicación / recepción de documentos -
asistente de despacho / jefe de CEDI - Control Entrega Documentos /
formato de control de entrega - firma de recibido / constancia de
recepción

**Condiciones de validación:** - Entrega física en el CEDI. - Firma del
asistente de despacho o del jefe de CEDI en el formato indicado. -
Evidencia de recepción.

**Reglas de decisión:** - Un correo electrónico o confirmación digital
no reemplaza la constancia física descrita. - Si existe sello o firma de
recepción en un formato equivalente, marcar REVISIÓN HUMANA para
confirmar que corresponde al control indicado. - Si no se aporta el
formato firmado, marcar NO IDENTIFICADO, no asumir que la entrega no
ocurrió.

**Búsqueda semántica sugerida:** `recibido en CEDI`,
`control de entrega de documentos`, `firma de despacho`,
`constancia de recepción física`.

## GC-23. Custodia de documentación

**Requisito fuente:** solicitar el contrato firmado por la obra. Cuando
la documentación física esté completa, entregarla al área
administrativa, responsable de custodia, control y archivo.

**Conceptos y expresiones relacionadas:** - contrato firmado por la obra
/ suscrito por el cliente / firma del contratante - documentos
originales / expediente físico - entrega a administración / traslado
documental - custodia / conservación / archivo / control documental

**Condiciones de validación:** - Se debe obtener el contrato firmado por
la obra/cliente. - Con la documentación física completa, debe entregarse
al área administrativa. - Administración debe asumir custodia, control y
archivo.

**Reglas de decisión:** - No confundir la firma de Interdoors con la
firma de la obra/cliente. - Si el contrato solo está firmado por
Interdoors, marcar PARCIAL. - La custodia requiere evidencia de entrega
o registro administrativo; una cláusula no demuestra que el expediente
físico se haya transferido.

**Búsqueda semántica sugerida:** `contrato suscrito por el cliente`,
`original firmado por la obra`,
`entrega de expediente a administración`, `custodia documental`.

## GC-24. Validación de anticipo y generación de pedido

**Requisito fuente:** antes de generar un pedido debe validarse el pago
del anticipo. Si el pedido se genera antes del pago, no puede enviarse a
fabricación hasta confirmar el abono. La gestión del anticipo debe
solicitarse al asesor comercial. Las excepciones deben validarse con
jefe administrativa o director comercial.

**Conceptos y expresiones relacionadas:** - anticipo pagado / abono
recibido / pago inicial confirmado - validación de pago / comprobante /
consignación / transferencia - generación de pedido / creación de orden
/ liberación del pedido - fabricación / producción / enviar a planta -
bloqueo / retención del pedido hasta el pago - asesor comercial /
gestión del anticipo - excepción / autorización administrativa /
aprobación comercial

**Condiciones de validación:** - Antes de generar el pedido, validar el
pago del anticipo. - Si el pedido se genera antes del pago, impedir su
envío a fabricación hasta confirmar el abono. - La gestión del anticipo
se solicita al asesor comercial. - Cualquier excepción requiere
validación del jefe administrativo o director comercial.

**Reglas de decisión:** - Diferenciar generación del pedido y liberación
para fabricación: el instructivo permite que el pedido se genere antes
del pago, pero prohíbe enviarlo a fabricar hasta confirmar el abono. -
Una promesa de pago no equivale a anticipo pagado. - Si se alega
excepción, exigir evidencia de validación del responsable indicado. - No
declarar que el anticipo fue pagado sin comprobante o confirmación
verificable.

**Búsqueda semántica sugerida:** `confirmación del abono`,
`anticipo recibido`, `pedido bloqueado para fabricación`,
`liberación de producción`, `validación previa del pago`.

## GC-25. Anexo de garantía

**Requisito fuente:** agregar la garantía de INTERDOORS como anexo al
contrato.

**Conceptos y expresiones relacionadas:** - garantía INTERDOORS /
garantía de Interdoors - anexo de garantía / documento de garantía
adjunto - condiciones de garantía / certificado de garantía - adjuntar /
incorporar / hacer parte integral del contrato

**Condiciones de validación:** - Debe estar incorporado o adjunto al
contrato el documento de garantía de INTERDOORS. - Debe existir
evidencia del anexo o de su incorporación como parte integral del
contrato.

**Reglas de decisión:** - Una mención genérica a que "los productos
tienen garantía" no demuestra que se anexó el documento. - Si el
contrato remite a un anexo que no fue suministrado, marcar PARCIAL y
solicitarlo. - No confundir este criterio (anexar la garantía de
INTERDOORS) con GC-14 (que los términos de garantía indiquen alcance,
vigencia y procedimiento de reclamación). Se relacionan, pero se
verifican por separado.

**Búsqueda semántica sugerida:** `garantía Interdoors adjunta`,
`anexo de garantía`, `documento de garantía hace parte del contrato`.

------------------------------------------------------------------------

# 3. Criterios que requieren evidencia fuera del contrato

Algunos puntos del instructivo describen actividades administrativas
posteriores o paralelas a la firma. No se pueden confirmar únicamente
leyendo el contrato. El sistema debe permitir incorporar otros archivos
como evidencia.

  -----------------------------------------------------------------------
  Criterios                           Evidencia que conviene analizar
  ----------------------------------- -----------------------------------
  GC-01                               Contrato físico, cotización,
                                      costeo, manual, documentos SST y
                                      anexos

  GC-07                               Contrato, cotización, pólizas y
                                      cuenta de cobro

  GC-11                               Contrato, lista de documentos de
                                      liquidación y soportes de cierre

  GC-15                               Firmas del director comercial y
                                      Gerencia

  GC-16                               Copias contractuales y cotizaciones
                                      firmadas

  GC-17                               Carpeta Bitácora, archivos
                                      escaneados y nombres de archivo

  GC-18                               Archivo "Relación de Contratos",
                                      fecha de actualización y firma

  GC-19                               Correo enviado, cuenta de cobro,
                                      pólizas y carpeta Bitácora

  GC-20                               Pólizas firmadas y archivos en
                                      Bitácora

  GC-21                               Correo al asesor, soportes adjuntos
                                      y constancia de entrega física

  GC-22                               Formato "Control Entrega
                                      Documentos" firmado

  GC-23                               Contrato firmado por la obra y
                                      constancia de entrega a
                                      Administración

  GC-24                               Comprobante de pago o confirmación
                                      del abono y estado del pedido

  GC-25                               Anexo de garantía de INTERDOORS
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 4. Diseño recomendado para el reconocimiento flexible

## 4.1 Capas de reconocimiento

Se recomienda que el script use varias capas, en este orden:

1.  **Búsqueda literal normalizada:** encuentra términos y frases
    directas después de normalizar mayúsculas, tildes, espacios y
    formatos.
2.  **Sinónimos y expresiones equivalentes:** compara el texto con los
    conceptos y expresiones relacionados de cada criterio.
3.  **Similitud semántica:** usa embeddings o un modelo de lenguaje para
    identificar frases con significado parecido aunque no compartan
    palabras.
4.  **Validación de condiciones:** comprueba porcentajes, plazos,
    responsables, eventos, documentos, negaciones y excepciones.
5.  **Decisión y trazabilidad:** asigna estado, confianza, evidencia
    textual y explicación.

La similitud semántica debe servir para encontrar candidatos, no para
aprobar automáticamente un requisito.

## 4.2 Umbrales iniciales orientativos

Estos valores son puntos de partida y deben calibrarse con contratos
reales revisados por una persona:

-   **0.85 a 1.00:** coincidencia semántica alta; pasar a validación de
    condiciones.
-   **0.70 a 0.84:** coincidencia probable; revisar condiciones y
    contexto.
-   **0.50 a 0.69:** coincidencia débil; enviar a revisión humana.
-   **Menor a 0.50:** no considerar coincidencia, salvo que la búsqueda
    literal encuentre evidencia.

No usar el umbral como único criterio de cumplimiento. Una similitud
alta no compensa un porcentaje incorrecto, una negación o una obligación
asignada a la parte equivocada.

## 4.3 Detección de contradicciones

El sistema debe buscar expresiones que cambian el sentido del requisito:

-   Negación: `no se reconocerá`, `no estará obligado`, `no aplica`.
-   Exclusividad: `únicamente`, `exclusivamente`, `solo`.
-   Condición: `siempre que`, `cuando`, `en caso de`, `sujeto a`.
-   Excepción: `salvo`, `excepto`, `a menos que`.
-   Aprobación: `previa autorización`, `con aprobación expresa`,
    `por escrito`.
-   Temporalidad: `antes de`, `después de`, `al momento de`,
    `dentro de`, `a partir de`.

Ejemplo: `El saldo se pagará contra instalación` no debe reconocerse
como equivalente a
`el saldo se facturará contra entrega del suministro`.

## 4.4 Resultado auditable

Por cada criterio, guardar: - identificador y nombre del criterio; -
estado; - nivel de confianza de la coincidencia; - texto exacto que
sirvió como evidencia; - documento y página; - condiciones verificadas,
no verificadas y contradictorias; - motivo del estado; - fecha de
análisis y versión de la base de conocimiento.

------------------------------------------------------------------------

# 5. Límites de interpretación del instructivo

-   El instructivo no define una lista exhaustiva de documentos de
    liquidación; no debe inventarse.
-   El instructivo no establece que todas las pólizas enumeradas
    apliquen en todos los contratos; indica "según corresponda".
-   Las excepciones deben validarse con los responsables señalados en el
    instructivo.
-   Los criterios de gestión documental, correos, firmas, entregas y
    custodia requieren evidencias administrativas adicionales al
    contrato.
-   GC-14 y GC-25 son criterios distintos: uno revisa el contenido de
    las condiciones de garantía y el otro la incorporación del documento
    de garantía de INTERDOORS.
-   GC-03, GC-04 y GC-05 están relacionados, pero deben evaluarse por
    separado.
-   GC-15 y GC-16 también están relacionados, pero verifican etapas y
    soportes diferentes.

**Regla final:** el sistema apoya la revisión y prioriza hallazgos; no
reemplaza la aprobación del director comercial, jefe administrativo,
analista de cartera o gerente general cuando el instructivo les asigna
esa responsabilidad.
