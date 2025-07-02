import mysql.connector
from typing import Optional, Dict, List
from datetime import datetime

class VotoDAO:
    """Data Access Object para operaciones relacionadas con votos"""
    
    @staticmethod
    def get_vote_by_cedula(connection: mysql.connector.MySQLConnection, cedula: str) -> Optional[Dict]:
        """Verificar si ya existe voto para esta cédula"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM votos WHERE cedula = %s"
            cursor.execute(query, (cedula,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    @staticmethod
    def create_vote(connection: mysql.connector.MySQLConnection, vote_data: Dict) -> int:
        """Crear nuevo voto"""
        cursor = connection.cursor()
        try:
            query = """
            INSERT INTO votos (cedula, candidato_id, timestamp, es_observado, estado_validacion, circuito_id, es_anulado)
            VALUES (%(cedula)s, %(candidato_id)s, %(timestamp)s, %(es_observado)s, %(estado_validacion)s, %(circuito_id)s, %(es_anulado)s)
            """
            cursor.execute(query, vote_data)
            return cursor.lastrowid
        finally:
            cursor.close()
    
    @staticmethod
    def get_observed_votes(connection: mysql.connector.MySQLConnection, circuito_id: int) -> List[Dict]:
        """Obtener votos observados pendientes"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
            SELECT id, cedula, candidato_id, timestamp
            FROM votos 
            WHERE es_observado = TRUE AND estado_validacion = 'pendiente' AND circuito_id = %s
            """
            cursor.execute(query, (circuito_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    @staticmethod
    def update_vote_validation(connection: mysql.connector.MySQLConnection, voto_id: int, estado: str) -> bool:
        """Actualizar estado de validación de voto observado"""
        cursor = connection.cursor()
        try:
            query = "UPDATE votos SET estado_validacion = %s WHERE id = %s"
            cursor.execute(query, (estado, voto_id))
            return cursor.rowcount > 0
        finally:
            cursor.close()
    
    @staticmethod
    def get_vote_by_id(connection: mysql.connector.MySQLConnection, voto_id: int) -> Optional[Dict]:
        """Obtener voto por ID"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM votos WHERE id = %s"
            cursor.execute(query, (voto_id,))
            return cursor.fetchone()
        finally:
            cursor.close()