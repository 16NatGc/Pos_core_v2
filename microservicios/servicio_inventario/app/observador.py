from abc import ABC, abstractmethod
from typing import List
from app.modelos import Producto

class ObservadorStock(ABC):
    @abstractmethod
    def actualizar_stock_bajo(self, producto: Producto):
        pass

class SujetoStock:
    def __init__(self):
        self._observadores: List[ObservadorStock] = []
        self._umbral_stock = 5
    
    def agregar_observador(self, observador: ObservadorStock):
        self._observadores.append(observador)
    
    def eliminar_observador(self, observador: ObservadorStock):
        self._observadores.remove(observador)
    
    def notificar_stock_bajo(self, producto: Producto):
        if producto.stock <= self._umbral_stock:
            for observador in self._observadores:
                observador.actualizar_stock_bajo(producto)

class NotificadorEmail(ObservadorStock):
    def actualizar_stock_bajo(self, producto: Producto):
        print(f"📧 ENVIANDO EMAIL: Stock bajo para {producto.nombre} - Stock actual: {producto.stock}")

class NotificadorLog(ObservadorStock):
    def actualizar_stock_bajo(self, producto: Producto):
        print(f"📝 LOG: Stock bajo detectado - Producto: {producto.nombre}, SKU: {producto.sku}, Stock: {producto.stock}")