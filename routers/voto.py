from fastapi import APIRouter, Depends
from services.voto_service import cast_vote, get_observed_votes, validate_observed_vote
from schemas import VotoRequest, VotoResponse, ValidarVotoRequest
from auth import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_token(token)

@router.post("/votar", response_model=VotoResponse)
async def votar(
    voto: VotoRequest,
    current_user: str = Depends(get_current_user)
):
    """Votar - requiere auth de mesa para determinar circuito"""
    return cast_vote(voto, current_user)

@router.get("/observados/{circuito}")
async def get_votos_observados(
    circuito: str,
    current_user: str = Depends(get_current_user)
):
    """Obtener votos observados pendientes para el circuito"""
    return get_observed_votes(circuito)

@router.post("/validar-observado")
async def validar_voto_observado(
    request: ValidarVotoRequest,
    current_user: str = Depends(get_current_user)
):
    """Validar o rechazar voto observado - solo presidente de mesa"""
    return validate_observed_vote(request.voto_id, request.accion)