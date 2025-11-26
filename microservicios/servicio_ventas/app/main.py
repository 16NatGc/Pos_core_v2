from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import httpx
from app.modelos import Venta, VentaCrear, DetalleVenta, EstadoVenta, ProductoInventario
from app.configuracion import configuracion
from app.estrategias import ContextoPago, FabricaEstrategiasPago
from typing import List, Dict, Any

app = FastAPI(
    title="Servicio de Ventas - POS Core",
    description="Microservicio para gestión de ventas y procesamiento de pagos",
    version="1.0.0"
)

# Conexión a MongoDB
cliente = MongoClient(configuracion.MONGODB_URL)
base_datos = cliente[configuracion.BASE_DATOS]
coleccion_ventas = base_datos[configuracion.COLECCION_VENTAS]
coleccion_detalles = base_datos[configuracion.COLECCION_DETALLE_VENTAS]

@app.get("/")
async def raiz():
    return {
        "servicio": "Ventas POS Core",
        "estado": "Funcionando",
        "version": "1.0.0",
        "patrones": ["Strategy"]
    }

@app.get("/salud")
async def salud():
    return {
        "estado": "Saludable",
        "servicio": "ventas",
        "base_datos": "MongoDB",
        "patrones_activos": ["Strategy"]
    }

async def obtener_producto_desde_inventario(producto_id: str, token: str) -> ProductoInventario:
    """Obtiene información del producto desde el servicio de inventario"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{configuracion.URL_INVENTARIO}/api/v1/productos/{producto_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            if response.status_code == 200:
                datos = response.json()
                return ProductoInventario(
                    id=datos["id"],
                    nombre=datos["nombre"],
                    precio=datos["precio"],
                    stock=datos["stock"],
                    sku=datos["sku"]
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Producto no encontrado en inventario: {producto_id}"
                )
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Servicio de inventario no disponible"
            )

async def actualizar_stock_inventario(producto_id: str, cantidad: int, token: str):
    """Actualiza el stock en el servicio de inventario"""
    async with httpx.AsyncClient() as client:
        try:
            # Obtener producto actual
            producto = await obtener_producto_desde_inventario(producto_id, token)
            
            # Verificar stock suficiente
            if producto.stock < cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {producto.nombre}. Stock actual: {producto.stock}, solicitado: {cantidad}"
                )
            
            # Actualizar stock
            nuevo_stock = producto.stock - cantidad
            response = await client.put(
                f"{configuracion.URL_INVENTARIO}/api/v1/productos/{producto_id}",
                json={"stock": nuevo_stock},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al actualizar stock: {response.text}"
                )
                
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Error comunicándose con servicio de inventario"
            )

@app.post("/api/v1/ventas", response_model=Venta, status_code=status.HTTP_201_CREATED)
async def crear_venta(venta: VentaCrear, authorization: str = None):
    try:
        # Extraer token del header
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Token de autenticación requerido"
            )
        token = authorization.replace("Bearer ", "")
        
        # Validar y procesar detalles de venta
        total_venta = 0.0
        detalles_procesados = []
        
        for detalle in venta.detalles:
            # Obtener información del producto desde inventario
            producto = await obtener_producto_desde_inventario(detalle.producto_id, token)
            
            # Verificar stock
            if producto.stock < detalle.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {producto.nombre}. Stock: {producto.stock}, Solicitado: {detalle.cantidad}"
                )
            
            # Calcular subtotal
            subtotal = detalle.cantidad * detalle.precio_unitario
            total_venta += subtotal
            
            # Crear detalle procesado
            detalle_procesado = {
                "producto_id": detalle.producto_id,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "sku": producto.sku,
                "subtotal": subtotal,
                "nombre_producto": producto.nombre
            }
            detalles_procesados.append(detalle_procesado)
        
        # 🎯 PATRÓN STRATEGY: Procesar pago
        contexto_pago = ContextoPago()
        estrategia = FabricaEstrategiasPago.crear_estrategia(venta.metodo_pago)
        contexto_pago.establecer_estrategia(estrategia)
        resultado_pago = contexto_pago.procesar_pago(total_venta, venta.datos_pago)
        
        # Crear documento de venta
        venta_dict = {
            "usuario_id": venta.usuario_id,
            "total": total_venta,
            "metodo_pago": venta.metodo_pago,
            "datos_pago": venta.datos_pago,
            "estado": EstadoVenta.COMPLETADA if resultado_pago["estado"] == "aprobado" else EstadoVenta.PENDIENTE,
            "resultado_pago": resultado_pago,
            "fecha_creacion": datetime.utcnow()
        }
        
        # Insertar venta
        resultado_venta = coleccion_ventas.insert_one(venta_dict)
        venta_id = str(resultado_venta.inserted_id)
        
        # Insertar detalles
        for detalle in detalles_procesados:
            detalle["venta_id"] = venta_id
            coleccion_detalles.insert_one(detalle)
            
            # Actualizar stock en inventario
            await actualizar_stock_inventario(detalle["producto_id"], detalle["cantidad"], token)
        
        # Retornar venta creada
        return Venta(
            id=venta_id,
            usuario_id=venta.usuario_id,
            detalles=[DetalleVenta(**detalle) for detalle in detalles_procesados],
            total=total_venta,
            metodo_pago=venta.metodo_pago,
            datos_pago=venta.datos_pago,
            estado=EstadoVenta.COMPLETADA if resultado_pago["estado"] == "aprobado" else EstadoVenta.PENDIENTE,
            fecha_creacion=venta_dict["fecha_creacion"],
            resultado_pago=resultado_pago
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear venta: {str(e)}"
        )

@app.get("/api/v1/ventas", response_model=List[Venta])
async def listar_ventas():
    try:
        ventas = []
        for documento in coleccion_ventas.find():
            # Obtener detalles de la venta
            detalles_docs = coleccion_detalles.find({"venta_id": str(documento["_id"])})
            detalles = [DetalleVenta(**detalle) for detalle in detalles_docs]
            
            venta = Venta(
                id=str(documento["_id"]),
                usuario_id=documento["usuario_id"],
                detalles=detalles,
                total=documento["total"],
                metodo_pago=documento["metodo_pago"],
                datos_pago=documento.get("datos_pago", {}),
                estado=documento["estado"],
                fecha_creacion=documento["fecha_creacion"],
                resultado_pago=documento.get("resultado_pago")
            )
            ventas.append(venta)
        return ventas
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar ventas: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)