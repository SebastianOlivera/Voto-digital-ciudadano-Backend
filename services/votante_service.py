from fastapi import HTTPException
from datetime import datetime
from database import get_db_connection, get_db_transaction
from dao.votante_dao import VotanteDAO
from dao.credencial_dao import CredencialDAO
from schemas import VoteEnableRequest, VotanteStatus

def enable_voter(request: VoteEnableRequest, current_user: str) -> dict:
    """Autorizar votante con verificación de circuito"""
    with get_db_transaction() as connection:
        # Para votos observados, usar la cédula real del votante
        cedula_a_autorizar = request.cedula_real if request.esEspecial and request.cedula_real else request.credencial
        
        # Verificar si ya está autorizado
        existing_auth = VotanteDAO.get_authorization(connection, cedula_a_autorizar)
        
        if existing_auth:
            raise HTTPException(status_code=400, detail="Votante ya autorizado")
        
        # Verificar si la cédula está autorizada para este circuito
        is_authorized_for_circuit = CredencialDAO.is_cedula_authorized_for_circuit(
            connection, cedula_a_autorizar, request.circuito
        )
        
        # Si no está autorizada para este circuito, debe ser voto observado
        if not is_authorized_for_circuit and not request.esEspecial:
            # Obtener el circuito correcto de la cédula
            circuito_correcto = CredencialDAO.get_circuito_by_cedula(connection, cedula_a_autorizar)
            circuito_msg = f" (pertenece al circuito {circuito_correcto['numero_circuito']})" if circuito_correcto else ""
            
            raise HTTPException(
                status_code=400, 
                detail=f"Cédula no autorizada para este circuito{circuito_msg}. Debe ser registrada como voto observado."
            )
        
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
        mensaje_extra = ""
        if not is_authorized_for_circuit and request.esEspecial:
            circuito_correcto = CredencialDAO.get_circuito_by_cedula(connection, cedula_a_autorizar)
            if circuito_correcto:
                mensaje_extra = f" (cédula pertenece al circuito {circuito_correcto['numero_circuito']})"
        
        return {"mensaje": f"Votante {cedula_a_autorizar} autorizado exitosamente para voto {tipo_voto}{mensaje_extra}"}

def get_voter_status(circuito: str, cedula: str) -> VotanteStatus:
    """Verificar estado de votante"""
    with get_db_connection() as connection:
        auth_record = VotanteDAO.get_authorization(connection, cedula, int(circuito))
        
        if not auth_record:
            raise HTTPException(status_code=404, detail="Votante no encontrado o no autorizado")
        
        return VotanteStatus(
            cedula=auth_record['cedula'],
            estado=auth_record['estado'],
            circuito_id=auth_record.get('circuito_id'),
            fecha_autorizacion=auth_record.get('fecha_autorizacion'),
            fecha_voto=auth_record.get('fecha_voto'),
            es_autorizacion_especial=auth_record.get('es_autorizacion_especial', False)
        )

def get_voters_by_circuit(circuito: str) -> list:
    """Listar votantes por circuito"""
    with get_db_connection() as connection:
        votantes = VotanteDAO.get_voters_by_circuit(connection, int(circuito))
        return [{"cedula": v["cedula"], "estado": v["estado"], "fecha_autorizacion": v["fecha_autorizacion"]} for v in votantes]