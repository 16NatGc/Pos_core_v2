from pydantic import BaseModel
from typing import Optional
from enum import Enum

class RolUsuario(str, Enum):
    ADMINISTRADOR = "administrador"
    CAJERO = "cajero"

class UsuarioBase(BaseModel):
    nombre: str
    usuario: str
    correo: Optional[str] = None
    rol: RolUsuario

class UsuarioCrear(UsuarioBase):
    contrasena: str

class Usuario(UsuarioBase):
    id: str
    activo: bool = True

class UsuarioLogin(BaseModel):
    usuario: str
    contrasena: str

# AGREGAR esta clase Token
class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: Usuario