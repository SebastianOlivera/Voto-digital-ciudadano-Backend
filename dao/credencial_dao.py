import mysql.connector
from typing import Optional, Dict, List

class CredencialDAO:
    """Data Access Object para operaciones relacionadas con credenciales autorizadas por circuito"""
    
    @staticmethod
    def get_circuito_by_cedula(connection: mysql.connector.MySQLConnection, cedula: str) -> Optional[Dict]:
        """Obtener el circuito asignado a una cédula"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
            SELECT c.numero_circuito, c.id as circuito_id, e.nombre as establecimiento_nombre
            FROM credenciales_autorizadas ca
            JOIN circuitos c ON ca.circuito_id = c.id
            JOIN establecimientos e ON c.establecimiento_id = e.id
            WHERE ca.cedula = %s
            """
            cursor.execute(query, (cedula,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    @staticmethod
    def is_cedula_authorized_for_circuit(connection: mysql.connector.MySQLConnection, cedula: str, circuito_numero: str) -> bool:
        """Verificar si una cédula está autorizada para votar en un circuito específico"""
        cursor = connection.cursor()
        try:
            query = """
            SELECT COUNT(*) as count
            FROM credenciales_autorizadas ca
            JOIN circuitos c ON ca.circuito_id = c.id
            WHERE ca.cedula = %s AND c.numero_circuito = %s
            """
            cursor.execute(query, (cedula, circuito_numero))
            result = cursor.fetchone()
            return result[0] > 0
        finally:
            cursor.close()
    
    @staticmethod
    def bulk_insert_credenciales(connection: mysql.connector.MySQLConnection, credenciales_data: List[Dict]) -> int:
        """Insertar múltiples credenciales desde CSV"""
        cursor = connection.cursor()
        inserted_count = 0
        try:
            for credencial in credenciales_data:
                circuito_numero = credencial['circuito_numero']
                
                # Verificar si el circuito existe
                check_query = "SELECT id FROM circuitos WHERE numero_circuito = %s"
                cursor.execute(check_query, (circuito_numero,))
                circuito_result = cursor.fetchone()
                
                if not circuito_result:
                    # El circuito no existe, crearlo junto con el establecimiento
                    print(f"Creando circuito {circuito_numero} y establecimiento")
                    
                    # Primero crear el establecimiento
                    establecimiento_query = """
                    INSERT INTO establecimientos (nombre, departamento, ciudad, direccion, tipo_establecimiento, accesible)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    establecimiento_data = (
                        credencial.get('establecimiento_nombre', f'Establecimiento {circuito_numero}'),
                        credencial.get('departamento', 'Sin especificar'),
                        credencial.get('ciudad', 'Sin especificar'), 
                        credencial.get('direccion', 'Sin especificar'),
                        'Escuela',
                        True
                    )
                    cursor.execute(establecimiento_query, establecimiento_data)
                    establecimiento_id = cursor.lastrowid
                    
                    # Luego crear el circuito
                    circuito_query = """
                    INSERT INTO circuitos (numero_circuito, establecimiento_id)
                    VALUES (%s, %s)
                    """
                    cursor.execute(circuito_query, (circuito_numero, establecimiento_id))
                    circuito_id = cursor.lastrowid
                    print(f"Circuito {circuito_numero} creado con ID {circuito_id}")
                else:
                    circuito_id = circuito_result[0]
                
                # Insertar la credencial autorizada
                insert_query = """
                INSERT IGNORE INTO credenciales_autorizadas (cedula, circuito_id)
                VALUES (%s, %s)
                """
                cursor.execute(insert_query, (credencial['cedula_autorizada'], circuito_id))
                
                # Verificar si se insertó (rowcount es 1 si se insertó, 0 si ya existía)
                if cursor.rowcount > 0:
                    inserted_count += 1
                    print(f"Insertada credencial {credencial['cedula_autorizada']} para circuito {circuito_numero}")
            
            return inserted_count
        finally:
            cursor.close()
    
    @staticmethod
    def get_credenciales_by_circuit(connection: mysql.connector.MySQLConnection, circuito_numero: str) -> List[Dict]:
        """Obtener todas las credenciales autorizadas para un circuito"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
            SELECT ca.cedula, ca.fecha_creacion
            FROM credenciales_autorizadas ca
            JOIN circuitos c ON ca.circuito_id = c.id
            WHERE c.numero_circuito = %s
            ORDER BY ca.cedula
            """
            cursor.execute(query, (circuito_numero,))
            return cursor.fetchall()
        finally:
            cursor.close()