import mysql.connector
from typing import Optional, Dict, List
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminDAO:
    """Data Access Object para operaciones administrativas"""
    
    @staticmethod
    def create_usuario(connection: mysql.connector.MySQLConnection, usuario_data: Dict) -> int:
        """Crear nuevo usuario de mesa o presidente"""
        cursor = connection.cursor()
        try:
            # Hash de la contraseña
            password_hash = pwd_context.hash(usuario_data['password'])
            
            query = """
            INSERT INTO usuarios (username, password_hash, circuito_id, role, is_active)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                usuario_data['username'],
                password_hash,
                usuario_data['circuito_id'],
                usuario_data['role'],
                True
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    
    @staticmethod
    def create_establecimiento(connection: mysql.connector.MySQLConnection, establecimiento_data: Dict) -> int:
        """Crear nuevo establecimiento"""
        cursor = connection.cursor()
        try:
            query = """
            INSERT INTO establecimientos (nombre, departamento, ciudad, zona, barrio, direccion, tipo_establecimiento, accesible)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                establecimiento_data['nombre'],
                establecimiento_data['departamento'],
                establecimiento_data['ciudad'],
                establecimiento_data.get('zona'),
                establecimiento_data.get('barrio'),
                establecimiento_data['direccion'],
                establecimiento_data['tipo_establecimiento'],
                establecimiento_data.get('accesible', True)
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    
    @staticmethod
    def create_eleccion(connection: mysql.connector.MySQLConnection, eleccion_data: Dict) -> bool:
        """Crear nueva elección con sus listas"""
        cursor = connection.cursor()
        try:
            # Primero crear la elección
            eleccion_query = """
            INSERT INTO elecciones (año, fecha_creacion)
            VALUES (%s, %s)
            """
            cursor.execute(eleccion_query, (eleccion_data['año'], datetime.now()))
            eleccion_id = cursor.lastrowid
            
            # Crear o obtener partidos y candidatos
            for lista in eleccion_data['listas']:
                # Crear o obtener partido
                partido_query = "SELECT id FROM partidos WHERE nombre = %s"
                cursor.execute(partido_query, (lista['partido'],))
                partido_result = cursor.fetchone()
                
                if partido_result:
                    partido_id = partido_result[0]
                else:
                    cursor.execute("INSERT INTO partidos (nombre) VALUES (%s)", (lista['partido'],))
                    partido_id = cursor.lastrowid
                
                # Crear candidato presidente
                candidato_query = """
                INSERT INTO candidatos (nombre, partido_id, es_presidente)
                VALUES (%s, %s, %s)
                """
                cursor.execute(candidato_query, (lista['candidato'], partido_id, True))
                candidato_id = cursor.lastrowid
                
                # Crear vicepresidente
                cursor.execute(candidato_query, (lista['vicepresidente'], partido_id, False))
                vicepresidente_id = cursor.lastrowid
                
                # Crear lista electoral
                lista_query = """
                INSERT INTO listas_electorales (numero_lista, candidato_presidente_id, candidato_vicepresidente_id, partido_id, eleccion_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(lista_query, (
                    lista['numero_lista'],
                    candidato_id,
                    vicepresidente_id,
                    partido_id,
                    eleccion_id
                ))
            
            return True
        finally:
            cursor.close()
    
    @staticmethod
    def create_circuito(connection: mysql.connector.MySQLConnection, circuito_data: Dict) -> int:
        """Crear nuevo circuito"""
        cursor = connection.cursor()
        try:
            query = """
            INSERT INTO circuitos (numero_circuito, numero_mesa, establecimiento_id)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (
                circuito_data['numero_circuito'],
                circuito_data['numero_mesa'],
                circuito_data['establecimiento_id']
            ))
            return cursor.lastrowid
        finally:
            cursor.close()
    
    @staticmethod
    def get_establecimientos_list(connection: mysql.connector.MySQLConnection) -> List[Dict]:
        """Obtener lista de establecimientos para selección"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
            SELECT id, nombre, departamento, ciudad, direccion
            FROM establecimientos
            ORDER BY departamento, ciudad, nombre
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    @staticmethod
    def get_circuitos_list(connection: mysql.connector.MySQLConnection) -> List[Dict]:
        """Obtener lista de circuitos con sus IDs reales"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
            SELECT c.id, c.numero_circuito, c.numero_mesa, 
                   e.nombre as establecimiento
            FROM circuitos c
            JOIN establecimientos e ON c.establecimiento_id = e.id
            ORDER BY c.numero_circuito
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    @staticmethod
    def username_exists(connection: mysql.connector.MySQLConnection, username: str) -> bool:
        """Verificar si un username ya existe"""
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
    
    @staticmethod
    def circuito_exists(connection: mysql.connector.MySQLConnection, numero_circuito: str) -> bool:
        """Verificar si un circuito ya existe"""
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM circuitos WHERE numero_circuito = %s", (numero_circuito,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()