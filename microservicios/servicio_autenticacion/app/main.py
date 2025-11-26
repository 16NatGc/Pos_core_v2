from fastapi import FastAPI
from app.rutas import router

app = FastAPI(
    title="Servicio de Autenticación - POS_CORE",
    description="Microservicio para gestión de usuarios y autenticación",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1", tags=["autenticacion"])

@app.get("/")
async def raiz():
    return {
        "servicio": "Autenticación POS_CORE",
        "estado": "Funcionando",
        "version": "1.0.0"
    }

@app.get("/salud")
async def salud():
    return {
        "estado": "Saludable",
        "servicio": "autenticacion",
        "base_datos": "MongoDB"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)