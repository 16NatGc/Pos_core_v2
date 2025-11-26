import os
from dotenv import load_dotenv

load_dotenv()

class Configuracion:
    MONGODB_URL = "mongodb://mongodb:27017"
    BASE_DATOS = "pos_core"
    COLECCION_PRODUCTOS = "productos"
    COLECCION_CATEGORIAS = "categorias"

configuracion = Configuracion()