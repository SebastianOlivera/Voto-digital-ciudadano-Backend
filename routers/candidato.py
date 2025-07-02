from fastapi import APIRouter
from typing import List
from services.candidato_service import get_candidates
from schemas import PartidoResponse

router = APIRouter()

@router.get("/", response_model=List[PartidoResponse])
async def get_candidatos():
    """Endpoint público - no requiere autenticación para que votantes vean candidatos"""
    return get_candidates()