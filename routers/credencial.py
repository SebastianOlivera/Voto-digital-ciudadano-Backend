from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import verify_token
from dao.credencial_dao import CredencialDAO
from database import get_db_connection
from typing import List, Dict

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_token(token)

@router.post("/upload-csv")
async def upload_credenciales_csv(
    credenciales_data: List[Dict],
    current_user: str = Depends(get_current_user)
):
    """Cargar credenciales desde CSV - solo superadmin"""
    try:
        with get_db_connection() as connection:
            count = CredencialDAO.bulk_insert_credenciales(connection, credenciales_data)
            connection.commit()
            return {"mensaje": f"Se cargaron {count} credenciales exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cargando credenciales: {str(e)}")

@router.get("/circuito/{credencial}")
async def get_circuito_by_credencial(
    credencial: str,
    current_user: str = Depends(get_current_user)
):
    """Obtener el circuito asignado a una credencial"""
    try:
        with get_db_connection() as connection:
            circuito_data = CredencialDAO.get_circuito_by_credencial(connection, credencial)
            if not circuito_data:
                raise HTTPException(status_code=404, detail="Credencial no encontrada en el sistema")
            return circuito_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando credencial: {str(e)}")

@router.get("/lista/{circuito_numero}")
async def get_credenciales_by_circuit(
    circuito_numero: str,
    current_user: str = Depends(get_current_user)
):
    """Listar credenciales autorizadas para un circuito"""
    try:
        with get_db_connection() as connection:
            credenciales = CredencialDAO.get_credenciales_by_circuit(connection, circuito_numero)
            return {"circuito": circuito_numero, "credenciales": credenciales}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo credenciales: {str(e)}")