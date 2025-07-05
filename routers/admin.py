from fastapi import APIRouter, Depends, HTTPException
from services.admin_service import create_usuario, create_establecimiento, create_eleccion, create_circuito, get_establecimientos, get_circuitos
from schemas import (
    CreateUsuarioRequest, CreateEstablecimientoRequest, CreateEleccionRequest, CreateCircuitoRequest,
    UsuarioCreatedResponse, EstablecimientoCreatedResponse
)
from auth import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_token(token)

@router.post("/usuario", response_model=UsuarioCreatedResponse)
async def crear_usuario(
    request: CreateUsuarioRequest,
    current_user: str = Depends(get_current_user)
):
    """Crear nuevo usuario (mesa o presidente) - solo para admin"""
    result = create_usuario(request)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/establecimiento", response_model=EstablecimientoCreatedResponse)
async def crear_establecimiento(
    request: CreateEstablecimientoRequest,
    current_user: str = Depends(get_current_user)
):
    """Crear nuevo establecimiento - solo para admin"""
    result = create_establecimiento(request)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/eleccion")
async def crear_eleccion(
    request: CreateEleccionRequest,
    current_user: str = Depends(get_current_user)
):
    """Crear nueva elección con listas - solo para admin"""
    result = create_eleccion(request)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/circuito")
async def crear_circuito(
    request: CreateCircuitoRequest,
    current_user: str = Depends(get_current_user)
):
    """Crear nuevo circuito - solo para admin"""
    result = create_circuito(request)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/establecimientos")
async def obtener_establecimientos(
    current_user: str = Depends(get_current_user)
):
    """Obtener lista de establecimientos"""
    return get_establecimientos()

@router.get("/circuitos")
async def obtener_circuitos(
    current_user: str = Depends(get_current_user)
):
    """Obtener lista de circuitos"""
    return get_circuitos()