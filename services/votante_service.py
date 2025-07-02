from fastapi import HTTPException
from datetime import datetime
from database import get_db_connection, get_db_transaction
from dao.votante_dao import VotanteDAO
from schemas import VoteEnableRequest, VotanteStatus

def enable_voter(request: VoteEnableRequest, current_user: str) -> dict:
    """Autorizar votante"""
    with get_db_transaction() as connection:
        # Para votos observados, usar la cédula real del votante
        cedula_a_autorizar = request.cedula_real if request.esEspecial and request.cedula_real else request.credencial
        
        # Verificar si ya está autorizado
        existing_auth = VotanteDAO.get_authorization(connection, cedula_a_autorizar)
        
        if existing_auth:
            raise HTTPException(status_code=400, detail="Votante ya autorizado")
        
        # Crear nueva autorización
        auth_data = {
            'cedula': cedula_a_autorizar,
            'circuito_id': int(request.circuito),
            'estado': 'HABILITADA',
            'autorizado_por': current_user,
            'fecha_autorizacion': datetime.now(),
            'es_autorizacion_especial': request.esEspecial or False
        }
        VotanteDAO.create_authorization(connection, auth_data)
        
        tipo_voto = "observado" if request.esEspecial else "normal"
        return {"mensaje": f"Votante {cedula_a_autorizar} autorizado exitosamente para voto {tipo_voto}"}

def get_voter_status(circuito: str, cedula: str) -> VotanteStatus:
    """Verificar estado de votante"""
    with get_db_connection() as connection:
        auth_record = VotanteDAO.get_authorization(connection, cedula, int(circuito))
        
        if not auth_record:
            raise HTTPException(status_code=404, detail="Votante no encontrado o no autorizado")
        
        return VotanteStatus(
            cedula=auth_record['cedula'],
            estado=auth_record['estado'],
            autorizado_por=auth_record['autorizado_por'],
            fecha_autorizacion=auth_record['fecha_autorizacion']
        )

def get_voters_by_circuit(circuito: str) -> list:
    """Listar votantes por circuito"""
    with get_db_connection() as connection:
        votantes = VotanteDAO.get_voters_by_circuit(connection, int(circuito))
        return [{"cedula": v["cedula"], "estado": v["estado"], "fecha_autorizacion": v["fecha_autorizacion"]} for v in votantes]