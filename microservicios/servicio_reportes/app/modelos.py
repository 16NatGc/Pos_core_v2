from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TipoReporte(str, Enum):
    VENTAS = "ventas"
    INVENTARIO = "inventario"
    RENDIMIENTO = "rendimiento"

class ParametrosReporte(BaseModel):
    tipo_reporte: TipoReporte
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    parametros_adicionales: Dict[str, Any] = {}

class RespuestaReporte(BaseModel):
    tipo_reporte: str
    fecha_generacion: str
    parametros: Dict[str, Any]
    datos: Dict[str, Any]