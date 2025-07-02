from fastapi import APIRouter, Depends
from services.mesa_service import close_circuit, close_mesa
from schemas import CerrarMesaRequest
from auth import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_token(token)

@router.patch("/{circuito}/close")
async def close_circuito(
    circuito: str,
    current_user: str = Depends(get_current_user)
):
    """Cerrar circuito - solo para mesa autenticada (compatibilidad)"""
    return close_circuit(circuito)

@router.post("/cerrar")
async def cerrar_mesa(
    request: CerrarMesaRequest,
    current_user: str = Depends(get_current_user)
):
    """Cerrar mesa - solo presidente de mesa"""
    return close_mesa(request.circuito)