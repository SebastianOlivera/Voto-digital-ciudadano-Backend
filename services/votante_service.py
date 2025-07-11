from fastapi import HTTPException
from datetime import datetime
from database import get_db_connection, get_db_transaction
from dao.votante_dao import VotanteDAO
from dao.credencial_dao import CredencialDAO
from schemas import VoteEnableRequest, VotanteStatus

def enable_voter(request: VoteEnableRequest, current_user: str) -> dict:
    """Autorizar votante con verificación de circuito"""
    with get_db_transaction() as connection:
        # Para votos observados, usar la credencial cívica del votante
        credencial_a_autorizar = request.credencial_civica if request.esEspecial and request.credencial_civica else request.credencial
        
        # Obtener el ID real del circuito a partir del número de circuito
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM circuitos WHERE numero_circuito = %s", (request.circuito,))
        circuito_db = cursor.fetchone()
        cursor.close()
        
        if not circuito_db:
            raise HTTPException(status_code=400, detail=f"Circuito {request.circuito} no encontrado")
        
        circuito_id = circuito_db['id']
        
        # Verificar si ya está autorizado
        existing_auth = VotanteDAO.get_authorization(connection, credencial_a_autorizar)
        
        if existing_auth:
            raise HTTPException(status_code=400, detail="Votante ya autorizado")
        
        # Verificar si la credencial está autorizada para este circuito
        is_authorized_for_circuit = CredencialDAO.is_credencial_authorized_for_circuit(
            connection, credencial_a_autorizar, request.circuito
        )
        
        # Si no está autorizada para este circuito, debe ser voto observado
        if not is_authorized_for_circuit and not request.esEspecial:
            # Obtener el circuito correcto de la credencial
            circuito_correcto = CredencialDAO.get_circuito_by_credencial(connection, credencial_a_autorizar)
            circuito_msg = f" (pertenece al circuito {circuito_correcto['numero_circuito']})" if circuito_correcto else ""
            
            raise HTTPException(
                status_code=400, 
                detail=f"Credencial no autorizada para este circuito{circuito_msg}. Debe ser registrada como voto observado."
            )
        
        # Crear nueva autorización
        auth_data = {
            'credencial': credencial_a_autorizar,
            'circuito_id': circuito_id,
            'estado': 'HABILITADA',
            'autorizado_por': current_user,
            'fecha_autorizacion': datetime.now(),
            'es_autorizacion_especial': request.esEspecial or False
        }
        VotanteDAO.create_authorization(connection, auth_data)
        
        tipo_voto = "observado" if request.esEspecial else "normal"
        mensaje_extra = ""
        if not is_authorized_for_circuit and request.esEspecial:
            circuito_correcto = CredencialDAO.get_circuito_by_credencial(connection, credencial_a_autorizar)
            if circuito_correcto:
                mensaje_extra = f" (credencial pertenece al circuito {circuito_correcto['numero_circuito']})"
        
        return {"mensaje": f"Votante {credencial_a_autorizar} autorizado exitosamente para voto {tipo_voto}{mensaje_extra}"}

def get_voter_status(circuito: str, credencial: str) -> VotanteStatus:
    """Verificar estado de votante"""
    with get_db_connection() as connection:
        # Obtener el ID real del circuito a partir del número de circuito
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM circuitos WHERE numero_circuito = %s", (circuito,))
        circuito_db = cursor.fetchone()
        cursor.close()
        
        if not circuito_db:
            raise HTTPException(status_code=404, detail=f"Circuito {circuito} no encontrado")
        
        circuito_id = circuito_db['id']
        # Primero buscar por circuito específico
        auth_record = VotanteDAO.get_authorization(connection, credencial, circuito_id)
        
        # Si no se encuentra, buscar sin filtro de circuito (para votos observados)
        if not auth_record:
            auth_record = VotanteDAO.get_authorization(connection, credencial)
        
        if not auth_record:
            raise HTTPException(status_code=404, detail="Votante no encontrado o no autorizado")
        
        return VotanteStatus(
            credencial=auth_record['credencial'],
            estado=auth_record['estado'],
            circuito_id=auth_record.get('circuito_id'),
            fecha_autorizacion=auth_record.get('fecha_autorizacion'),
            fecha_voto=auth_record.get('fecha_voto'),
            es_autorizacion_especial=auth_record.get('es_autorizacion_especial', False)
        )

def get_voters_by_circuit(circuito: str) -> list:
    """Listar votantes por circuito"""
    with get_db_connection() as connection:
        # Obtener el ID real del circuito a partir del número de circuito
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM circuitos WHERE numero_circuito = %s", (circuito,))
        circuito_db = cursor.fetchone()
        cursor.close()
        
        if not circuito_db:
            return []
        
        circuito_id = circuito_db['id']
        votantes = VotanteDAO.get_voters_by_circuit(connection, circuito_id)
        return [{"credencial": v["credencial"], "estado": v["estado"], "fecha_autorizacion": v["fecha_autorizacion"]} for v in votantes]