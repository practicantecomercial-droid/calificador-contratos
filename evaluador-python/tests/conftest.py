import pytest

from engine.document_reader import leer_texto

TEXTO_ERP = """Empresa
NIT
Dirección
Teléfono
Ciudad
CONSTRUCCIONES BUEN VIVIR S.A.S.
900085546
Carrera 45 # 108a - 50 Oficina 501
746 0395
BOGOTÁ D.C.
Fecha y hora de impresión: 05/03/2026 04:16 pm
CONTRATO NO. 2780477
Contratista
Contratista:
INTERDOORS SAS
NIT/CC:
900682082
Dirección:
AUT NORTE KM 26
Teléfono:
4602582
Email:
jose.puertas@interdoors.com.co
Ciudad:
GIRARDOTA
Contrato Detallado Por Grupos
Proyecto:
DIRECTOS - HEROES VIVIENDA
Tipo Contrato:
SUMINISTRO DE MATERIALES OBRA
Valor Contrato:
17,746,429.54
Estado:
Por Aprobación
Otrosi Contrato:
Fecha Inicio:
04/03/2026
Fecha Terminacion:
30/04/2026
Forma de Pago:
Referencia:
% Administracion:
0.00 %
0.00
% Imprevistos:
0.00 %
0.00
% Utilidad:
0.00 %
0.00
% Ret Garantias:
10 %
% IVA:
19 %
2,833,463.54
% Ret Anticipo:
30 %
Descripcion:
SUMINISTRO DE PUERTAS CARPINTERIA MADERA PARA ZONAS COMUNES
Observaciones:
EL TIEMPO DE ENTREGA SERAN 30 DIAS CALENDARIO COMO MAXIMO. GARANTIAS Y SEGUROS: - POLIZA DE
BUEN MANEJO DE ANTICIPO: Correspondiente a un 30% del valor antes de IVA ($4.473.889)
- POLIZA DE CUMPLIMIENTO: Correspondiente a un 20% del valor ($3.549.286)
- CALIDAD DEL MATERIALES: Correspondiente a un 20% del valor ($3.549.286)
CANTIDADES DE OBRA
Item
UM
"""


@pytest.fixture
def texto_erp():
    return TEXTO_ERP


@pytest.fixture
def documento_erp():
    return leer_texto(TEXTO_ERP, nombre="2780477.txt")
