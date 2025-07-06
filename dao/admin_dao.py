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
        """Crear nueva elección con sus listas - FULL WIPE de todos los datos excepto admin"""
        cursor = connection.cursor()
        try:
            # FULL WIPE - Limpiar todos los datos previos (excepto admin) en orden correcto
            print("🧹 Iniciando limpieza completa de datos...")
            
            # Deshabilitar foreign key checks temporalmente para facilitar la limpieza
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # 1. Limpiar votos y autorizaciones (sin dependencias)
            cursor.execute("DELETE FROM votos")
            cursor.execute("DELETE FROM autorizaciones") 
            cursor.execute("DELETE FROM credenciales_autorizadas")
            print("✓ Votos, autorizaciones y credenciales limpiadas")
            
            # 2. Limpiar usuarios (excepto admin) - preservar admin por username y role
            cursor.execute("DELETE FROM usuarios WHERE role != 'superadmin' AND username != 'admin'")
            print("✓ Usuarios de mesa y presidente eliminados (admin preservado)")
            
            # 3. Limpiar candidatos y elecciones anteriores
            cursor.execute("DELETE FROM candidatos")
            cursor.execute("DELETE FROM elecciones")
            print("✓ Candidatos y elecciones anteriores eliminadas")
            
            # 4. Limpiar circuitos (dependen de establecimientos)
            cursor.execute("DELETE FROM circuitos")
            print("✓ Circuitos eliminados")
            
            # 5. Limpiar establecimientos
            cursor.execute("DELETE FROM establecimientos")
            print("✓ Establecimientos eliminados")
            
            # Reactivar foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            print("🎯 Limpieza completa finalizada - Sistema completamente limpio")
            
            # Crear nueva elección
            eleccion_query = """
            INSERT INTO elecciones (año, nombre, activa, fecha_creacion)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(eleccion_query, (
                eleccion_data['año'], 
                f"Elección {eleccion_data['año']}", 
                True, 
                datetime.now()
            ))
            eleccion_id = cursor.lastrowid
            print(f"✓ Nueva elección {eleccion_data['año']} creada con ID {eleccion_id}")
            
            # Crear candidatos para cada lista
            for lista in eleccion_data['listas']:
                # Verificar que el partido existe
                cursor.execute("SELECT id FROM partidos WHERE id = %s", (lista['partido_id'],))
                if not cursor.fetchone():
                    continue
                
                # Crear candidato presidente
                candidato_query = """
                INSERT INTO candidatos (nombre, partido_id, es_presidente, numero_lista, eleccion_id, orden_lista)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(candidato_query, (
                    lista['candidato'], 
                    lista['partido_id'], 
                    True, 
                    lista['numero_lista'], 
                    eleccion_id,
                    1
                ))
                
                # Crear vicepresidente
                cursor.execute(candidato_query, (
                    lista['vicepresidente'], 
                    lista['partido_id'], 
                    False, 
                    lista['numero_lista'], 
                    eleccion_id,
                    2
                ))
            
            return True
        finally:
            cursor.close()
    
    @staticmethod
    def get_partidos_list(connection: mysql.connector.MySQLConnection) -> List[Dict]:
        """Obtener lista de partidos para selección"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
            SELECT id, nombre
            FROM partidos
            ORDER BY nombre
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    @staticmethod
    def create_partido(connection: mysql.connector.MySQLConnection, partido_data: Dict) -> Dict:
        """Crear nuevo partido"""
        cursor = connection.cursor(dictionary=True)
        try:
            # Verificar si ya existe el partido
            check_query = "SELECT id FROM partidos WHERE nombre = %s"
            cursor.execute(check_query, (partido_data['nombre'],))
            if cursor.fetchone():
                raise ValueError(f"Ya existe un partido con el nombre '{partido_data['nombre']}'")
            
            # Crear el partido
            query = """
            INSERT INTO partidos (nombre) 
            VALUES (%(nombre)s)
            """
            cursor.execute(query, partido_data)
            partido_id = cursor.lastrowid
            
            # Obtener el partido creado
            cursor.execute("SELECT * FROM partidos WHERE id = %s", (partido_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
    def create_circuito(connection: mysql.connector.MySQLConnection, circuito_data: Dict) -> int:
        """Crear nuevo circuito"""
        cursor = connection.cursor()
        try:
            query = """
            INSERT INTO circuitos (numero_circuito, establecimiento_id)
            VALUES (%s, %s)
            """
            cursor.execute(query, (
                circuito_data['numero_circuito'],
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
            SELECT c.id, c.numero_circuito, 
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