from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from jose import JWTError, jwt
from typing import Optional
from app.fabricas import ServicioFactory  # PATRÓN FACTORY METHOD

app = FastAPI(
    title="POS Core API Gateway", 
    version="2.0.0",
    description="Gateway principal con patrones de diseño GoF"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de servicios para Factory
SERVICIOS_CONFIG = {
    "autenticacion": {
        "url": "http://servicio_autenticacion:8000",
        "timeout": 30,
        "nombre": "Servicio de Autenticación"
    },
    "inventario": {
        "url": "http://servicio_inventario:8000", 
        "timeout": 30,
        "nombre": "Servicio de Inventario"
    },
    "ventas": {
        "url": "http://servicio_ventas:8000",
        "timeout": 30,
        "nombre": "Servicio de Ventas"
    },
    "reportes": {
        "url": "http://servicio_reportes:8000",
        "timeout": 30,
        "nombre": "Servicio de Reportes"
    }
}

# PATRÓN FACTORY METHOD: Crear servicios
servicios = {}
for nombre, config in SERVICIOS_CONFIG.items():
    try:
        servicios[nombre] = ServicioFactory.crear_servicio(nombre, config)
        print(f"Servicio creado con Factory: {nombre}")
    except ValueError as e:
        print(f"Servicio no disponible: {nombre} - {e}")

# Clave secreta para JWT
JWT_SECRET = "pos_core_2025"
JWT_ALGORITHM = "HS256"

async def obtener_token(request: Request) -> Optional[str]:
    """Extrae el token del header Authorization"""
    autorizacion = request.headers.get("Authorization")
    if autorizacion and autorizacion.startswith("Bearer "):
        return autorizacion.replace("Bearer ", "")
    return None

async def verificar_token(token: str = Depends(obtener_token)):
    """Verifica y decodifica el token JWT"""
    if not token:
        raise HTTPException(
            status_code=401, 
            detail="Token de autenticación requerido"
        )
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Token inválido: {str(e)}"
        )

# Health check general
@app.get("/")
async def raiz():
    return {
        "mensaje": "POS Core API Gateway", 
        "estado": "activo",
        "version": "2.0.0",
        "patrones": ["Factory Method", "Singleton", "Observer"]
    }

# Health check de servicios usando Factory
@app.get("/health")
async def health_check():
    salud_servicios = {}
    
    for nombre, servicio in servicios.items():
        try:
            resultado = await servicio.health_check()
            salud_servicios[nombre] = resultado
        except Exception as e:
            salud_servicios[nombre] = {"estado": "error", "error": str(e)}
    
    return {
        "gateway": "activo",
        "patrones_implementados": ["Factory Method", "Singleton", "Observer"],
        "servicios": salud_servicios
    }

# Ruta de autenticación (PÚBLICA)
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_autenticacion(request: Request, path: str):
    if "autenticacion" not in servicios:
        raise HTTPException(status_code=503, detail="Servicio de autenticación no disponible")
    
    servicio = servicios["autenticacion"]
    
    if request.method == "POST":
        if path == "registrar":
            body = await request.json()
            return await servicio.registrar_usuario(body)
        elif path == "login":
            body = await request.json()
            return await servicio.login(body)
    
    # Para otras rutas de autenticación
    async with httpx.AsyncClient() as client:
        url = f"{servicio.url_base}/api/v1/{path}"
        
        if request.method == "GET":
            response = await client.get(url, params=dict(request.query_params))
        elif request.method == "POST":
            body = await request.json()
            response = await client.post(url, json=body)
        elif request.method == "PUT":
            body = await request.json()
            response = await client.put(url, json=body)
        else:
            response = await client.delete(url)
        
        return JSONResponse(content=response.json(), status_code=response.status_code)

# Rutas protegidas para otros servicios
@app.api_route("/api/{servicio}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_protegido(
    request: Request, 
    servicio: str, 
    path: str, 
    token_payload: dict = Depends(verificar_token)
):
    if servicio not in servicios:
        raise HTTPException(status_code=404, detail=f"Servicio '{servicio}' no encontrado")
    
    servicio_obj = servicios[servicio]
    token = await obtener_token(request)
    
    if request.method == "POST" and path == "productos" and servicio == "inventario":
        body = await request.json()
        return await servicio_obj.crear_producto(body, token)
    
    elif request.method == "GET" and path == "productos" and servicio == "inventario":
        return await servicio_obj.listar_productos(token)
    
    # Para otras rutas
    async with httpx.AsyncClient() as client:
        url = f"{servicio_obj.url_base}/api/v1/{path}"
        headers = {"Authorization": f"Bearer {token}"}
        
        if request.method == "GET":
            response = await client.get(url, params=dict(request.query_params), headers=headers)
        elif request.method == "POST":
            body = await request.json()
            response = await client.post(url, json=body, headers=headers)
        elif request.method == "PUT":
            body = await request.json()
            response = await client.put(url, json=body, headers=headers)
        else:
            response = await client.delete(url, headers=headers)
        
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)