from fastapi import APIRouter, Depends
from services.votante_service import enable_voter, get_voter_status, get_voters_by_circuit
from schemas import VoteEnableRequest, VotanteStatus
from auth import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_token(token)

@router.post("/enable")
async def enable_vote(
    request: VoteEnableRequest,
    current_user: str = Depends(get_current_user)
):
    """Autorizar votante - solo mesa autenticada"""
    return enable_voter(request, current_user)

@router.get("/{circuito}/{credencial}", response_model=VotanteStatus)
async def get_votante(
    circuito: str,
    credencial: str
):
    """Verificar estado de votante - no requiere auth para cabina"""
    return get_voter_status(circuito, credencial)

@router.get("/{circuito}")
async def get_votantes_por_circuito(
    circuito: str,
    current_user: str = Depends(get_current_user)
):
    """Listar votantes por circuito - solo para mesa autenticada"""
    return get_voters_by_circuit(circuito)