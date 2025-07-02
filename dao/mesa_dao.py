import mysql.connector
from typing import Optional, Dict, List
from datetime import datetime

class MesaDAO:
    """Data Access Object para operaciones relacionadas con mesas"""
    
    @staticmethod
    def get_by_username(connection: mysql.connector.MySQLConnection, username: str) -> Optional[Dict]:
        """Obtener usuario de mesa por username"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
            SELECT u.id, u.username, u.password_hash, u.circuito_id, u.role,
                   c.numero_circuito, 
                   e.id as establecimiento_id, e.nombre as establecimiento_nombre,
                   e.departamento, e.ciudad, e.zona, e.barrio, e.direccion,
                   e.tipo_establecimiento, e.accesible
            FROM usuarios u
            JOIN circuitos c ON u.circuito_id = c.id
            JOIN establecimientos e ON c.establecimiento_id = e.id
            WHERE u.username = %s
            """
            cursor.execute(query, (username,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    @staticmethod
    def create_user(connection: mysql.connector.MySQLConnection, user_data: Dict) -> int:
        """Crear nuevo usuario de mesa"""
        cursor = connection.cursor()
        try:
            query = """
            INSERT INTO usuarios (username, password_hash, circuito_id, role)
            VALUES (%(username)s, %(password_hash)s, %(circuito_id)s, %(role)s)
            """
            cursor.execute(query, user_data)
            return cursor.lastrowid
        finally:
            cursor.close()
    
    @staticmethod
    def close_mesa(connection: mysql.connector.MySQLConnection, circuito_id: int) -> bool:
        """Cerrar mesa del circuito"""
        cursor = connection.cursor()
        try:
            # Actualizar estado de la mesa como cerrada
            query = """
            UPDATE usuarios 
            SET mesa_cerrada = TRUE, fecha_cierre = %s 
            WHERE circuito_id = %s
            """
            cursor.execute(query, (datetime.now(), circuito_id))
            return cursor.rowcount > 0
        finally:
            cursor.close()