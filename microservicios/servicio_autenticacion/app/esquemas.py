from pymongo import MongoClient
from bson import ObjectId
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.modelos import Usuario, UsuarioCrear, Token
from app.configuracion import configuracion
from typing import Optional

# PATRÓN SINGLETON para conexión MongoDB
class ConexionMongoDB:
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.cliente = MongoClient(configuracion.MONGODB_URL)
            print(" NUEVA INSTANCIA de ConexionMongoDB creada")
        return cls._instancia
    
    def obtener_db(self):
        return self.cliente[configuracion.BASE_DATOS]

# Configuración de encriptación
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Usar Singleton para conexión
conexion = ConexionMongoDB()
base_datos = conexion.obtener_db()
coleccion_usuarios = base_datos[configuracion.COLECCION_USUARIOS]

# Funciones de utilidad
def verificar_contrasena(contrasena_plana, contrasena_hash):
    return pwd_context.verify(contrasena_plana, contrasena_hash)

def obtener_hash_contrasena(contrasena):
    return pwd_context.hash(contrasena)

def crear_token_acceso(usuario: Usuario):
    expiracion = datetime.utcnow() + timedelta(seconds=configuracion.JWT_EXPIRACION)
    
    datos = {
        "sub": usuario.usuario,
        "rol": usuario.rol,
        "exp": expiracion
    }
    
    token = jwt.encode(datos, configuracion.JWT_SECRET, algorithm=configuracion.JWT_ALGORITHM)
    
    return Token(
        access_token=token,
        token_type="bearer",
        usuario=usuario
    )

def autenticar_usuario(usuario: str, contrasena: str):
    documento = coleccion_usuarios.find_one({"usuario": usuario})
    if not documento:
        return None
    if not verificar_contrasena(contrasena, documento["contrasena"]):
        return None
    
    return Usuario(
        id=str(documento["_id"]),
        nombre=documento["nombre"],
        usuario=documento["usuario"],
        correo=documento.get("correo"),
        rol=documento["rol"],
        activo=documento.get("activo", True)
    )

def obtener_usuario_por_nombre(usuario: str):
    documento = coleccion_usuarios.find_one({"usuario": usuario})
    if documento:
        return Usuario(
            id=str(documento["_id"]),
            nombre=documento["nombre"],
            usuario=documento["usuario"],
            correo=documento.get("correo"),
            rol=documento["rol"],
            activo=documento.get("activo", True)
        )
    return None

def obtener_usuario_por_id(usuario_id: str):
    try:
        documento = coleccion_usuarios.find_one({"_id": ObjectId(usuario_id)})
        if documento:
            return Usuario(
                id=str(documento["_id"]),
                nombre=documento["nombre"],
                usuario=documento["usuario"],
                correo=documento.get("correo"),
                rol=documento["rol"],
                activo=documento.get("activo", True)
            )
        return None
    except:
        return None

def crear_usuario(usuario: UsuarioCrear):
    usuario_dict = usuario.dict()
    usuario_dict["contrasena"] = obtener_hash_contrasena(usuario.contrasena)
    usuario_dict["fecha_creacion"] = datetime.utcnow()
    usuario_dict["activo"] = True
    
    resultado = coleccion_usuarios.insert_one(usuario_dict)
    
    return Usuario(
        id=str(resultado.inserted_id),
        nombre=usuario.nombre,
        usuario=usuario.usuario,
        correo=usuario.correo,
        rol=usuario.rol,
        activo=True
    )