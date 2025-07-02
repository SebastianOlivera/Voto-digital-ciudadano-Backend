import mysql.connector
from typing import Optional, Dict, List
from datetime import datetime

class VotanteDAO:
    """Data Access Object para operaciones relacionadas con votantes"""
    
    @staticmethod
    def get_authorization(connection: mysql.connector.MySQLConnection, cedula: str, circuito_id: int = None) -> Optional[Dict]:
        """Obtener autorización de votante"""
        cursor = connection.cursor(dictionary=True)
        try:
            if circuito_id:
                query = """
                SELECT * FROM autorizaciones 
                WHERE cedula = %s AND circuito_id = %s
                """
                cursor.execute(query, (cedula, circuito_id))
            else:
                query = """
                SELECT * FROM autorizaciones 
                WHERE cedula = %s
                """
                cursor.execute(query, (cedula,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    @staticmethod
    def create_authorization(connection: mysql.connector.MySQLConnection, auth_data: Dict) -> int:
        """Crear nueva autorización"""
        cursor = connection.cursor()
        try:
            query = """
            INSERT INTO autorizaciones (cedula, circuito_id, estado, autorizado_por, fecha_autorizacion, es_autorizacion_especial)
            VALUES (%(cedula)s, %(circuito_id)s, %(estado)s, %(autorizado_por)s, %(fecha_autorizacion)s, %(es_autorizacion_especial)s)
            """
            cursor.execute(query, auth_data)
            return cursor.lastrowid
        finally:
            cursor.close()
    
    @staticmethod
    def update_authorization_status(connection: mysql.connector.MySQLConnection, cedula: str, estado: str, fecha_voto: datetime = None) -> bool:
        """Actualizar estado de autorización"""
        cursor = connection.cursor()
        try:
            if fecha_voto:
                query = """
                UPDATE autorizaciones 
                SET estado = %s, fecha_voto = %s 
                WHERE cedula = %s
                """
                cursor.execute(query, (estado, fecha_voto, cedula))
            else:
                query = """
                UPDATE autorizaciones 
                SET estado = %s 
                WHERE cedula = %s
                """
                cursor.execute(query, (estado, cedula))
            return cursor.rowcount > 0
        finally:
            cursor.close()
    
    @staticmethod
    def get_voters_by_circuit(connection: mysql.connector.MySQLConnection, circuito_id: int) -> List[Dict]:
        """Obtener votantes por circuito"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
            SELECT cedula, estado, fecha_autorizacion 
            FROM autorizaciones 
            WHERE circuito_id = %s
            """
            cursor.execute(query, (circuito_id,))
            return cursor.fetchall()
        finally:
            cursor.close()