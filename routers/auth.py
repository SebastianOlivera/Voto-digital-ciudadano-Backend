from fastapi import APIRouter, Form
from services.auth_service import authenticate_user
from schemas import LoginResponse

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """Endpoint de autenticación para mesas"""
    return authenticate_user(username, password)