from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime, timedelta
import httpx

# PATRON TEMPLATE METHOD
class PlantillaReporte(ABC):
    def generar_reporte(self, parametros: Dict[str, Any], token: str) -> Dict[str, Any]:
        """Template method - define el esqueleto del algoritmo"""
        self.validar_parametros(parametros)
        datos = self.obtener_datos(parametros, token)
        datos_procesados = self.procesar_datos(datos, parametros)
        formato = self.formatear_reporte(datos_procesados, parametros)
        return self.estructurar_respuesta(formato, parametros)
    
    def validar_parametros(self, parametros: Dict[str, Any]):
        """Hook opcional - validación básica"""
        if 'fecha_inicio' in parametros and 'fecha_fin' in parametros:
            fecha_inicio = datetime.fromisoformat(parametros['fecha_inicio'])
            fecha_fin = datetime.fromisoformat(parametros['fecha_fin'])
            if fecha_fin < fecha_inicio:
                raise ValueError("La fecha fin no puede ser anterior a la fecha inicio")
    
    @abstractmethod
    def obtener_datos(self, parametros: Dict[str, Any], token: str) -> Any:
        """Obtener datos específicos del reporte"""
        pass
    
    @abstractmethod
    def procesar_datos(self, datos: Any, parametros: Dict[str, Any]) -> Any:
        """Procesar datos según el tipo de reporte"""
        pass
    
    def formatear_reporte(self, datos: Any, parametros: Dict[str, Any]) -> Any:
        """Hook opcional - formateo específico"""
        return datos
    
    def estructurar_respuesta(self, datos: Any, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """Estructura final del reporte"""
        return {
            "tipo_reporte": self.__class__.__name__,
            "fecha_generacion": datetime.utcnow().isoformat(),
            "parametros": parametros,
            "datos": datos
        }

# REPORTES CONCRETOS
class ReporteVentas(PlantillaReporte):
    def obtener_datos(self, parametros: Dict[str, Any], token: str) -> List[Dict[str, Any]]:
        """Obtener datos de ventas del servicio correspondiente"""
        async def fetch_ventas():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{configuracion.URL_VENTAS}/api/v1/ventas",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30.0
                )
                return response.json()
        
        # Nota: En producción usarías async/await adecuadamente
        import asyncio
        return asyncio.run(fetch_ventas())
    
    def procesar_datos(self, datos: List[Dict[str, Any]], parametros: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar datos de ventas para el reporte"""
        if not datos:
            return {"total_ventas": 0, "ventas_por_metodo": {}, "productos_vendidos": []}
        
        fecha_inicio = datetime.fromisoformat(parametros.get('fecha_inicio', '2000-01-01'))
        fecha_fin = datetime.fromisoformat(parametros.get('fecha_fin', '2100-01-01'))
        
        ventas_filtradas = [
            venta for venta in datos 
            if fecha_inicio <= datetime.fromisoformat(venta['fecha_creacion']) <= fecha_fin
        ]
        
        total_ventas = sum(venta['total'] for venta in ventas_filtradas)
        
        ventas_por_metodo = {}
        for venta in ventas_filtradas:
            metodo = venta['metodo_pago']
            ventas_por_metodo[metodo] = ventas_por_metodo.get(metodo, 0) + venta['total']
        
        productos_vendidos = {}
        for venta in ventas_filtradas:
            for detalle in venta.get('detalles', []):
                producto = detalle.get('nombre_producto', 'Desconocido')
                productos_vendidos[producto] = productos_vendidos.get(producto, 0) + detalle['cantidad']
        
        return {
            "total_ventas": total_ventas,
            "cantidad_ventas": len(ventas_filtradas),
            "ventas_por_metodo": ventas_por_metodo,
            "productos_mas_vendidos": sorted(
                productos_vendidos.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            "ventas": ventas_filtradas
        }

class ReporteInventario(PlantillaReporte):
    def obtener_datos(self, parametros: Dict[str, Any], token: str) -> List[Dict[str, Any]]:
        """Obtener datos de inventario"""
        async def fetch_inventario():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{configuracion.URL_INVENTARIO}/api/v1/productos",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30.0
                )
                return response.json()
        
        import asyncio
        return asyncio.run(fetch_inventario())
    
    def procesar_datos(self, datos: List[Dict[str, Any]], parametros: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar datos de inventario"""
        if not datos:
            return {"total_productos": 0, "stock_bajo": [], "valor_inventario": 0}
        
        productos_stock_bajo = [prod for prod in datos if prod['stock'] <= 5]
        valor_total_inventario = sum(prod['precio'] * prod['stock'] for prod in datos)
        
        return {
            "total_productos": len(datos),
            "productos_activos": len([p for p in datos if p.get('activo', True)]),
            "stock_bajo": [
                {
                    "nombre": p['nombre'],
                    "stock_actual": p['stock'],
                    "sku": p['sku']
                } for p in productos_stock_bajo
            ],
            "valor_inventario": valor_total_inventario,
            "productos_por_categoria": self._agrupar_por_categoria(datos)
        }
    
    def _agrupar_por_categoria(self, productos: List[Dict[str, Any]]) -> Dict[str, int]:
        categorias = {}
        for producto in productos:
            categoria = producto.get('categoria', 'Sin categoría')
            categorias[categoria] = categorias.get(categoria, 0) + 1
        return categorias

class ReporteRendimiento(PlantillaReporte):
    def obtener_datos(self, parametros: Dict[str, Any], token: str) -> Dict[str, Any]:
        """Obtener datos de múltiples servicios"""
        async def fetch_datos():
            async with httpx.AsyncClient() as client:
                # Obtener ventas
                ventas_response = await client.get(
                    f"{configuracion.URL_VENTAS}/api/v1/ventas",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30.0
                )
                
                # Obtener inventario
                inventario_response = await client.get(
                    f"{configuracion.URL_INVENTARIO}/api/v1/productos",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30.0
                )
                
                return {
                    "ventas": ventas_response.json(),
                    "inventario": inventario_response.json()
                }
        
        import asyncio
        return asyncio.run(fetch_datos())
    
    def procesar_datos(self, datos: Dict[str, Any], parametros: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar datos para reporte de rendimiento"""
        ventas = datos.get('ventas', [])
        inventario = datos.get('inventario', [])
        
        fecha_inicio = datetime.fromisoformat(parametros.get('fecha_inicio', '2000-01-01'))
        fecha_fin = datetime.fromisoformat(parametros.get('fecha_fin', '2100-01-01'))
        
        ventas_periodo = [
            venta for venta in ventas 
            if fecha_inicio <= datetime.fromisoformat(venta['fecha_creacion']) <= fecha_fin
        ]
        
        return {
            "metricas_ventas": {
                "total_periodo": sum(v['total'] for v in ventas_periodo),
                "ventas_totales": len(ventas),
                "ticket_promedio": self._calcular_ticket_promedio(ventas_periodo)
            },
            "metricas_inventario": {
                "total_productos": len(inventario),
                "valor_inventario": sum(p['precio'] * p['stock'] for p in inventario),
                "productos_stock_bajo": len([p for p in inventario if p['stock'] <= 5])
            },
            "periodo_analizado": {
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat()
            }
        }
    
    def _calcular_ticket_promedio(self, ventas: List[Dict[str, Any]]) -> float:
        if not ventas:
            return 0.0
        return sum(venta['total'] for venta in ventas) / len(ventas)

# Factory para reportes
class FabricaReportes:
    @staticmethod
    def crear_reporte(tipo: str) -> PlantillaReporte:
        if tipo == "ventas":
            return ReporteVentas()
        elif tipo == "inventario":
            return ReporteInventario()
        elif tipo == "rendimiento":
            return ReporteRendimiento()
        else:
            raise ValueError(f"Tipo de reporte no soportado: {tipo}")