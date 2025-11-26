import os
from dotenv import load_dotenv

load_dotenv()

class Configuracion:
    MONGODB_URL = "mongodb://mongodb:27017"
    BASE_DATOS = "pos_core"
    COLECCION_USUARIOS = "usuarios"
    
    JWT_SECRET = "mi_clave_secreta_pos_core_2025"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRACION = 24 * 60 * 60

configuracion = Configuracion()