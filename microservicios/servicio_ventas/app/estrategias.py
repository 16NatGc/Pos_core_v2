from abc import ABC, abstractmethod
from typing import Dict, Any

class EstrategiaPago(ABC):
    @abstractmethod
    def procesar_pago(self, monto: float, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        pass

class EstrategiaTarjetaCredito(EstrategiaPago):
    def procesar_pago(self, monto: float, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Procesando pago con tarjeta: ${monto:.2f}")
        return {
            "estado": "aprobado",
            "metodo": "tarjeta_credito",
            "monto": monto,
            "referencia": f"TXN_{id(datos_pago)}_{monto}",
            "mensaje": "Pago con tarjeta procesado exitosamente"
        }

class EstrategiaEfectivo(EstrategiaPago):
    def procesar_pago(self, monto: float, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Procesando pago en efectivo: ${monto:.2f}")
        return {
            "estado": "aprobado",
            "metodo": "efectivo",
            "monto": monto,
            "cambio": datos_pago.get("monto_entregado", monto) - monto,
            "mensaje": "Pago en efectivo registrado"
        }

class EstrategiaTransferencia(EstrategiaPago):
    def procesar_pago(self, monto: float, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Procesando transferencia: ${monto:.2f}")
        return {
            "estado": "pendiente",
            "metodo": "transferencia",
            "monto": monto,
            "referencia": datos_pago.get("referencia", f"TRF_{id(datos_pago)}"),
            "mensaje": "Transferencia en proceso de verificacion"
        }

class ContextoPago:
    def __init__(self):
        self._estrategia = None
    
    def establecer_estrategia(self, estrategia: EstrategiaPago):
        self._estrategia = estrategia
    
    def procesar_pago(self, monto: float, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        if self._estrategia is None:
            raise ValueError("Estrategia de pago no establecida")
        return self._estrategia.procesar_pago(monto, datos_pago)

class FabricaEstrategiasPago:
    @staticmethod
    def crear_estrategia(tipo: str) -> EstrategiaPago:
        if tipo == "tarjeta":
            return EstrategiaTarjetaCredito()
        elif tipo == "efectivo":
            return EstrategiaEfectivo()
        elif tipo == "transferencia":
            return EstrategiaTransferencia()
        else:
            raise ValueError(f"Metodo de pago no soportado: {tipo}")