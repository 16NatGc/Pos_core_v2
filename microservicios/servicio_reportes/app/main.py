from fastapi import FastAPI, HTTPException, Header
from app.modelos import ParametrosReporte, RespuestaReporte
from app.plantillas import FabricaReportes
from app.configuracion import configuracion
from typing import Dict, Any

app = FastAPI(
    title="Servicio de Reportes - POS Core",
    description="Microservicio para generacion de reportes con Template Method",
    version="1.0.0"
)

@app.get("/")
async def raiz():
    return {
        "servicio": "Reportes POS Core",
        "estado": "Funcionando",
        "version": "1.0.0",
        "patrones": ["Template Method"]
    }

@app.get("/salud")
async def salud():
    return {
        "estado": "Saludable",
        "servicio": "reportes",
        "patrones_activos": ["Template Method"]
    }

@app.post("/api/v1/reportes/generar", response_model=RespuestaReporte)
async def generar_reporte(
    parametros: ParametrosReporte,
    authorization: str = Header(None)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Token de autenticacion requerido"
            )
        
        token = authorization.replace("Bearer ", "")
        
        # PATRON TEMPLATE METHOD: Crear y ejecutar reporte
        reporte = FabricaReportes.crear_reporte(parametros.tipo_reporte)
        
        # Preparar parametros
        parametros_dict = parametros.dict()
        if parametros_dict.get('fecha_inicio') is None:
            parametros_dict['fecha_inicio'] = '2000-01-01'
        if parametros_dict.get('fecha_fin') is None:
            parametros_dict['fecha_fin'] = '2100-01-01'
        
        # Generar reporte usando el template method
        resultado = reporte.generar_reporte(parametros_dict, token)
        
        return RespuestaReporte(**resultado)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar reporte: {str(e)}"
        )

@app.get("/api/v1/reportes/tipos")
async def obtener_tipos_reportes():
    return {
        "tipos_disponibles": [
            {
                "tipo": "ventas",
                "descripcion": "Reporte de ventas por periodo",
                "parametros": ["fecha_inicio", "fecha_fin"]
            },
            {
                "tipo": "inventario",
                "descripcion": "Reporte de estado de inventario",
                "parametros": []
            },
            {
                "tipo": "rendimiento",
                "descripcion": "Reporte de rendimiento general",
                "parametros": ["fecha_inicio", "fecha_fin"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)