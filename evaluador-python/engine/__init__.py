"""Motor de reconocimiento semántico de contratos (Interdoors)."""
from .expediente import combinar_resultados, evaluar_expediente
from .pipeline import (
    evaluar_archivo,
    evaluar_archivo_con_expediente,
    evaluar_documento,
    evaluar_documento_con_expediente,
)

__all__ = [
    "combinar_resultados",
    "evaluar_archivo",
    "evaluar_archivo_con_expediente",
    "evaluar_documento",
    "evaluar_documento_con_expediente",
    "evaluar_expediente",
]
