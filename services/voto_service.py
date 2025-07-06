from fastapi import HTTPException
from datetime import datetime
from typing import Optional
from database import get_db_connection, get_db_transaction
from dao.mesa_dao import MesaDAO
from dao.votante_dao import VotanteDAO
from dao.voto_dao import VotoDAO
from schemas import VotoRequest, VotoResponse
import random
import string

def generate_comprobante(circuito_id: int) -> str:
    """Generar número de comprobante único para el circuito"""
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            # Obtener el último número secuencial para este circuito
            query = """
            SELECT numero_comprobante FROM votos 
            WHERE circuito_id = %s AND numero_comprobante LIKE %s
            ORDER BY id DESC LIMIT 1
            """
            pattern = f"C{circuito_id:03d}-%"
            cursor.execute(query, (circuito_id, pattern))
            result = cursor.fetchone()
            
            if result:
                # Extraer el número secuencial del último comprobante
                last_comprobante = result[0]
                last_number = int(last_comprobante.split('-')[1])
                next_number = last_number + 1
            else:
                # Primer voto del circuito
                next_number = 1
            
            return f"C{circuito_id:03d}-{next_number:05d}"
        finally:
            cursor.close()

def cast_vote(voto: VotoRequest, current_user: str) -> VotoResponse:
    """Registrar voto"""
    with get_db_transaction() as connection:
        # Obtener información de la mesa que registra el voto
        mesa_user = MesaDAO.get_by_username(connection, current_user)
        if not mesa_user:
            raise HTTPException(status_code=403, detail="Usuario de mesa no encontrado")
        
        circuito_id = mesa_user['circuito_id']
        
        # Para votos observados, buscar también con credencial en lugar de credencial_civica
        auth_record = VotanteDAO.get_authorization(connection, voto.credencial)
        if not auth_record or auth_record['estado'] not in ['HABILITADA']:
            raise HTTPException(status_code=403, detail="Votante no autorizado para votar")
        
        # Verificar que no haya votado ya (usando tabla autorizaciones)
        if auth_record['estado'] == 'VOTÓ':
            raise HTTPException(status_code=400, detail="Esta credencial ya ha votado")
    
        # Generar comprobante único
        numero_comprobante = generate_comprobante(circuito_id)
        
        # Determinar si es voto observado basado en la autorización especial
        es_observado = auth_record.get('es_autorizacion_especial', False)
        estado_validacion = 'pendiente' if es_observado else 'aprobado'
        
        # Registrar voto
        # -1 = voto anulado, 0 = voto en blanco, >0 = candidato válido
        candidato_final = None
        es_anulado = False
        
        if voto.candidato_id == -1:
            es_anulado = True
            candidato_final = None
        elif voto.candidato_id == 0:
            candidato_final = None
        else:
            candidato_final = voto.candidato_id
        
        vote_data = {
            'numero_comprobante': numero_comprobante,
            'candidato_id': candidato_final,
            'timestamp': datetime.now(),
            'es_observado': es_observado,
            'estado_validacion': estado_validacion,
            'circuito_id': circuito_id,
            'es_anulado': es_anulado
        }
        VotoDAO.create_vote(connection, vote_data)
        
        # Actualizar estado de autorización
        VotanteDAO.update_authorization_status(connection, voto.credencial, 'VOTÓ', datetime.now())
    
        mensaje = f"Voto registrado exitosamente. Comprobante: {numero_comprobante}"
        if es_observado:
            mensaje += f" (VOTO OBSERVADO - Circuito credencial: {auth_record['circuito_id']}, Circuito mesa: {circuito_id})"
        
        return VotoResponse(mensaje=mensaje)

def get_observed_votes(circuito: str) -> list:
    """Obtener votos observados pendientes para el circuito"""
    with get_db_connection() as connection:
        votos = VotoDAO.get_observed_votes(connection, int(circuito))
        
        return [
            {
                "id": voto["id"],
                "numero_comprobante": voto["numero_comprobante"],
                "candidato_id": voto["candidato_id"],
                "fecha_hora": voto["timestamp"].isoformat()
            }
            for voto in votos
        ]

def validate_observed_vote(voto_id: int, accion: str) -> dict:
    """Validar o rechazar voto observado"""
    with get_db_transaction() as connection:
        voto = VotoDAO.get_vote_by_id(connection, voto_id)
        if not voto:
            raise HTTPException(status_code=404, detail="Voto no encontrado")
        
        if accion == "validar":
            estado = "aprobado"
        elif accion == "rechazar":
            estado = "rechazado"
        else:
            raise HTTPException(status_code=400, detail="Acción no válida")
        
        VotoDAO.update_vote_validation(connection, voto_id, estado)
        return {"mensaje": f"Voto {accion}o exitosamente"}