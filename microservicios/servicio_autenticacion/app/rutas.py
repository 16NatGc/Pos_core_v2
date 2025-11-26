from fastapi import APIRouter, HTTPException
from app.modelos import UsuarioCrear, UsuarioLogin, Usuario
from app import esquemas  # Importar el módulo completo

router = APIRouter()

@router.post("/registrar", response_model=Usuario)
def registrar_usuario(usuario: UsuarioCrear):
    try:
        usuario_existente = esquemas.obtener_usuario_por_nombre(usuario.usuario)
        if usuario_existente:
            raise HTTPException(
                status_code=400,
                detail="El nombre de usuario ya está registrado"
            )
        
        nuevo_usuario = esquemas.crear_usuario(usuario)
        return nuevo_usuario
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar usuario: {str(e)}")

@router.post("/login", response_model=esquemas.Token)
def login(credenciales: UsuarioLogin):
    try:
        usuario = esquemas.autenticar_usuario(credenciales.usuario, credenciales.contrasena)
        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Credenciales incorrectas"
            )
        
        token = esquemas.crear_token_acceso(usuario)
        return token
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en login: {str(e)}")

@router.get("/usuarios/{usuario_id}", response_model=Usuario)
def obtener_usuario(usuario_id: str):
    try:
        usuario = esquemas.obtener_usuario_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

@router.get("/usuarios", response_model=list[Usuario])
def listar_usuarios():
    try:
        usuarios = []
        for documento in esquemas.coleccion_usuarios.find():
            usuarios.append(Usuario(
                id=str(documento["_id"]),
                nombre=documento["nombre"],
                usuario=documento["usuario"],
                correo=documento.get("correo"),
                rol=documento["rol"],
                activo=documento.get("activo", True)
            ))
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar usuarios: {str(e)}")