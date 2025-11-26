from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CategoriaProducto(str, Enum):
    ELECTRONICA = "electronica"
    ROPA = "ropa"
    ALIMENTOS = "alimentos"
    HOGAR = "hogar"
    OFICINA = "oficina"

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    categoria: CategoriaProducto
    sku: str = Field(..., min_length=1, max_length=50)

class ProductoCrear(ProductoBase):
    pass

class Producto(ProductoBase):
    id: str
    fecha_creacion: datetime
    activo: bool = True

    class Config:
        from_attributes = True

class ProductoActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    categoria: Optional[CategoriaProducto] = None

class Categoria(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None
    activa: bool = True