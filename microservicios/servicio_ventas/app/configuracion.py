import os
from dotenv import load_dotenv

load_dotenv()

class Configuracion:
    MONGODB_URL = "mongodb://mongodb:27017"
    BASE_DATOS = "pos_core"
    COLECCION_VENTAS = "ventas"
    COLECCION_DETALLE_VENTAS = "detalle_ventas"
    URL_INVENTARIO = "http://servicio_inventario:8000"

configuracion = Configuracion()