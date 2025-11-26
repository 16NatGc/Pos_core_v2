from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MetodoPago(str, Enum):
    TARJETA = "tarjeta"
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"

class EstadoVenta(str, Enum):
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

class DetalleVentaBase(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., gt=0)
    sku: str

class DetalleVenta(DetalleVentaBase):
    id: str
    subtotal: float

class VentaBase(BaseModel):
    usuario_id: str
    detalles: List[DetalleVentaBase]
    metodo_pago: MetodoPago
    datos_pago: Dict[str, Any] = {}

class VentaCrear(VentaBase):
    pass

class Venta(VentaBase):
    id: str
    total: float
    estado: EstadoVenta
    fecha_creacion: datetime
    resultado_pago: Optional[Dict[str, Any]] = None

class ProductoInventario(BaseModel):
    id: str
    nombre: str
    precio: float
    stock: int
    sku: str