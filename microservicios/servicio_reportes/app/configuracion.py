import os
from dotenv import load_dotenv

load_dotenv()

class Configuracion:
    MONGODB_URL = "mongodb://mongodb:27017"
    BASE_DATOS = "pos_core"
    URL_VENTAS = "http://servicio_ventas:8000"
    URL_INVENTARIO = "http://servicio_inventario:8000"

configuracion = Configuracion()