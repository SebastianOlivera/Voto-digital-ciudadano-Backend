import mysql.connector
from typing import List, Dict

class CandidatoDAO:
    """Data Access Object para operaciones relacionadas con candidatos"""
    
    @staticmethod
    def get_all_with_parties(connection: mysql.connector.MySQLConnection) -> List[Dict]:
        """Obtener todos los candidatos con sus partidos"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
            SELECT c.id, c.nombre as candidato_nombre, c.orden_lista, p.nombre as partido_nombre
            FROM candidatos c
            JOIN partidos p ON c.partido_id = p.id
            ORDER BY p.nombre, c.orden_lista
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()