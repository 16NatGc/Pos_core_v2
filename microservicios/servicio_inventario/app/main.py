from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from app.modelos import Producto, ProductoCrear, ProductoActualizar
from app.configuracion import configuracion
from app.observador import SujetoStock, NotificadorEmail, NotificadorLog
from typing import List

app = FastAPI(
    title="Servicio de Inventario - POS Core",
    description="Microservicio para gestión de productos e inventario",
    version="1.0.0"
)

# Conexión a MongoDB
cliente = MongoClient(configuracion.MONGODB_URL)
base_datos = cliente[configuracion.BASE_DATOS]
coleccion_productos = base_datos[configuracion.COLECCION_PRODUCTOS]

# Patrón Observer para notificaciones de stock
sujeto_stock = SujetoStock()
sujeto_stock.agregar_observador(NotificadorEmail())
sujeto_stock.agregar_observador(NotificadorLog())

@app.get("/")
async def raiz():
    return {
        "servicio": "Inventario POS Core",
        "estado": "Funcionando",
        "version": "1.0.0"
    }

@app.get("/salud")
async def salud():
    return {
        "estado": "Saludable",
        "servicio": "inventario",
        "base_datos": "MongoDB"
    }

@app.post("/api/v1/productos", response_model=Producto, status_code=status.HTTP_201_CREATED)
async def crear_producto(producto: ProductoCrear):
    try:
        # Verificar si el SKU ya existe
        producto_existente = coleccion_productos.find_one({"sku": producto.sku, "activo": True})
        if producto_existente:
            raise HTTPException(
                status_code=400,
                detail="El SKU ya está registrado"
            )
        
        # Crear documento del producto
        producto_dict = producto.dict()
        producto_dict["fecha_creacion"] = datetime.utcnow()
        producto_dict["activo"] = True
        
        # Insertar en la base de datos
        resultado = coleccion_productos.insert_one(producto_dict)
        
        # Crear objeto Producto para retornar
        producto_creado = Producto(
            id=str(resultado.inserted_id),
            **producto_dict
        )
        
        # 🔔 PATRÓN OBSERVER: Notificar si el stock es bajo
        sujeto_stock.notificar_stock_bajo(producto_creado)
        
        return producto_creado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear producto: {str(e)}"
        )

@app.get("/api/v1/productos", response_model=List[Producto])
async def listar_productos():
    try:
        productos = []
        for documento in coleccion_productos.find({"activo": True}):
            producto = Producto(
                id=str(documento["_id"]),
                nombre=documento["nombre"],
                descripcion=documento.get("descripcion"),
                precio=documento["precio"],
                stock=documento["stock"],
                categoria=documento["categoria"],
                sku=documento["sku"],
                fecha_creacion=documento["fecha_creacion"],
                activo=documento["activo"]
            )
            productos.append(producto)
        return productos
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al listar productos: {str(e)}"
        )

@app.get("/api/v1/productos/{producto_id}", response_model=Producto)
async def obtener_producto(producto_id: str):
    try:
        documento = coleccion_productos.find_one({"_id": ObjectId(producto_id), "activo": True})
        if not documento:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado"
            )
        
        producto = Producto(
            id=str(documento["_id"]),
            nombre=documento["nombre"],
            descripcion=documento.get("descripcion"),
            precio=documento["precio"],
            stock=documento["stock"],
            categoria=documento["categoria"],
            sku=documento["sku"],
            fecha_creacion=documento["fecha_creacion"],
            activo=documento["activo"]
        )
        
        # 🔔 PATRÓN OBSERVER: Verificar stock bajo al obtener producto
        sujeto_stock.notificar_stock_bajo(producto)
        
        return producto
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"ID de producto inválido: {str(e)}"
        )

@app.put("/api/v1/productos/{producto_id}", response_model=Producto)
async def actualizar_producto(producto_id: str, producto_actualizar: ProductoActualizar):
    try:
        # Verificar que el producto existe
        producto_existente = coleccion_productos.find_one({"_id": ObjectId(producto_id), "activo": True})
        if not producto_existente:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado"
            )
        
        # Preparar datos para actualizar
        datos_actualizar = {k: v for k, v in producto_actualizar.dict().items() if v is not None}
        
        if not datos_actualizar:
            raise HTTPException(
                status_code=400,
                detail="No hay datos para actualizar"
            )
        
        # Actualizar en la base de datos
        coleccion_productos.update_one(
            {"_id": ObjectId(producto_id)},
            {"$set": datos_actualizar}
        )
        
        # Obtener el producto actualizado
        producto_actualizado = coleccion_productos.find_one({"_id": ObjectId(producto_id)})
        
        producto = Producto(
            id=str(producto_actualizado["_id"]),
            nombre=producto_actualizado["nombre"],
            descripcion=producto_actualizado.get("descripcion"),
            precio=producto_actualizado["precio"],
            stock=producto_actualizado["stock"],
            categoria=producto_actualizado["categoria"],
            sku=producto_actualizado["sku"],
            fecha_creacion=producto_actualizado["fecha_creacion"],
            activo=producto_actualizado["activo"]
        )
        
        # 🔔 PATRÓN OBSERVER: Verificar stock después de actualizar
        sujeto_stock.notificar_stock_bajo(producto)
        
        return producto
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar producto: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)