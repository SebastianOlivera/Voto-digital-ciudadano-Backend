import mysql.connector
from typing import List, Dict, Optional

class ResultadoDAO:
    """Data Access Object para operaciones relacionadas con resultados"""
    
    @staticmethod
    def get_votes_by_candidate(connection: mysql.connector.MySQLConnection, departamento: Optional[str] = None) -> List[Dict]:
        """Obtener votos por candidato"""
        cursor = connection.cursor(dictionary=True)
        try:
            # Obtener la elección activa
            cursor.execute("SELECT id FROM elecciones WHERE activa = TRUE LIMIT 1")
            eleccion_activa = cursor.fetchone()
            
            if not eleccion_activa:
                return []
            
            if departamento:
                query = """
                SELECT c.nombre as candidato, p.nombre as partido, COUNT(v.id) as votos
                FROM candidatos c
                JOIN partidos p ON c.partido_id = p.id
                LEFT JOIN votos v ON c.id = v.candidato_id AND v.estado_validacion = 'aprobado'
                LEFT JOIN circuitos ci ON v.circuito_id = ci.id
                LEFT JOIN establecimientos e ON ci.establecimiento_id = e.id
                WHERE (e.departamento = %s OR v.id IS NULL) AND c.es_presidente = TRUE AND c.eleccion_id = %s
                GROUP BY c.id, c.nombre, p.nombre
                ORDER BY votos DESC
                """
                cursor.execute(query, (departamento, eleccion_activa['id']))
            else:
                query = """
                SELECT c.nombre as candidato, p.nombre as partido, COUNT(v.id) as votos
                FROM candidatos c
                JOIN partidos p ON c.partido_id = p.id
                LEFT JOIN votos v ON c.id = v.candidato_id AND v.estado_validacion = 'aprobado'
                WHERE c.es_presidente = TRUE AND c.eleccion_id = %s
                GROUP BY c.id, c.nombre, p.nombre
                ORDER BY votos DESC
                """
                cursor.execute(query, (eleccion_activa['id'],))
            
            resultados = cursor.fetchall()
            return resultados
        finally:
            cursor.close()
    
    @staticmethod
    def get_blank_votes(connection: mysql.connector.MySQLConnection, departamento: Optional[str] = None) -> int:
        """Obtener votos en blanco"""
        cursor = connection.cursor()
        try:
            # Obtener la elección activa
            cursor.execute("SELECT id FROM elecciones WHERE activa = TRUE LIMIT 1")
            eleccion_activa = cursor.fetchone()
            
            if not eleccion_activa:
                return 0
            
            # Verificar si hay algún voto para candidatos de la elección activa
            cursor.execute("""
                SELECT COUNT(*) FROM votos v 
                JOIN candidatos c ON v.candidato_id = c.id 
                WHERE c.eleccion_id = %s AND v.estado_validacion = 'aprobado'
            """, (eleccion_activa[0],))
            
            votos_eleccion_activa = cursor.fetchone()[0]
            
            # Si no hay votos de la elección activa, devolver 0
            if votos_eleccion_activa == 0:
                return 0
            
            if departamento:
                query = """
                SELECT COUNT(v.id)
                FROM votos v
                JOIN circuitos c ON v.circuito_id = c.id
                JOIN establecimientos e ON c.establecimiento_id = e.id
                WHERE v.candidato_id IS NULL AND v.es_anulado = FALSE 
                AND v.estado_validacion = 'aprobado' AND e.departamento = %s
                """
                cursor.execute(query, (departamento,))
            else:
                query = """
                SELECT COUNT(v.id)
                FROM votos v
                WHERE v.candidato_id IS NULL AND v.es_anulado = FALSE AND v.estado_validacion = 'aprobado'
                """
                cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
    
    @staticmethod
    def get_nullified_votes(connection: mysql.connector.MySQLConnection, departamento: Optional[str] = None) -> int:
        """Obtener votos anulados"""
        cursor = connection.cursor()
        try:
            # Obtener la elección activa
            cursor.execute("SELECT id FROM elecciones WHERE activa = TRUE LIMIT 1")
            eleccion_activa = cursor.fetchone()
            
            if not eleccion_activa:
                return 0
            
            # Verificar si hay algún voto para candidatos de la elección activa
            cursor.execute("""
                SELECT COUNT(*) FROM votos v 
                JOIN candidatos c ON v.candidato_id = c.id 
                WHERE c.eleccion_id = %s AND v.estado_validacion = 'aprobado'
            """, (eleccion_activa[0],))
            
            votos_eleccion_activa = cursor.fetchone()[0]
            
            # Si no hay votos de la elección activa, devolver 0
            if votos_eleccion_activa == 0:
                return 0
            
            if departamento:
                query = """
                SELECT COUNT(v.id)
                FROM votos v
                JOIN circuitos c ON v.circuito_id = c.id
                JOIN establecimientos e ON c.establecimiento_id = e.id
                LEFT JOIN candidatos ca ON v.candidato_id = ca.id
                WHERE v.es_anulado = TRUE AND v.estado_validacion = 'aprobado' AND e.departamento = %s
                AND (v.candidato_id IS NULL OR ca.eleccion_id = %s)
                """
                cursor.execute(query, (departamento, eleccion_activa[0]))
            else:
                query = """
                SELECT COUNT(v.id)
                FROM votos v
                LEFT JOIN candidatos ca ON v.candidato_id = ca.id
                WHERE v.es_anulado = TRUE AND v.estado_validacion = 'aprobado'
                AND (v.candidato_id IS NULL OR ca.eleccion_id = %s)
                """
                cursor.execute(query, (eleccion_activa[0],))
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
    
    @staticmethod
    def get_total_votes(connection: mysql.connector.MySQLConnection, departamento: Optional[str] = None) -> int:
        """Obtener total de votos"""
        cursor = connection.cursor()
        try:
            # Obtener la elección activa
            cursor.execute("SELECT id FROM elecciones WHERE activa = TRUE LIMIT 1")
            eleccion_activa = cursor.fetchone()
            
            if not eleccion_activa:
                return 0
            
            # Verificar si hay algún voto para candidatos de la elección activa
            cursor.execute("""
                SELECT COUNT(*) FROM votos v 
                JOIN candidatos c ON v.candidato_id = c.id 
                WHERE c.eleccion_id = %s AND v.estado_validacion = 'aprobado'
            """, (eleccion_activa[0],))
            
            votos_eleccion_activa = cursor.fetchone()[0]
            
            # Si no hay votos de la elección activa, devolver 0
            if votos_eleccion_activa == 0:
                return 0
            
            if departamento:
                query = """
                SELECT COUNT(v.id)
                FROM votos v
                JOIN circuitos c ON v.circuito_id = c.id
                JOIN establecimientos e ON c.establecimiento_id = e.id
                LEFT JOIN candidatos ca ON v.candidato_id = ca.id
                WHERE v.estado_validacion = 'aprobado' AND e.departamento = %s
                AND (v.candidato_id IS NULL OR ca.eleccion_id = %s)
                """
                cursor.execute(query, (departamento, eleccion_activa[0]))
            else:
                query = """
                SELECT COUNT(v.id)
                FROM votos v
                LEFT JOIN candidatos ca ON v.candidato_id = ca.id
                WHERE v.estado_validacion = 'aprobado'
                AND (v.candidato_id IS NULL OR ca.eleccion_id = %s)
                """
                cursor.execute(query, (eleccion_activa[0],))
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
    
    @staticmethod
    def get_total_voters(connection: mysql.connector.MySQLConnection, departamento: Optional[str] = None) -> int:
        """Obtener total de votantes autorizados"""
        cursor = connection.cursor()
        try:
            if departamento:
                query = """
                SELECT COUNT(a.id)
                FROM autorizaciones a
                JOIN circuitos c ON a.circuito_id = c.id
                JOIN establecimientos e ON c.establecimiento_id = e.id
                WHERE e.departamento = %s
                """
                cursor.execute(query, (departamento,))
            else:
                query = "SELECT COUNT(id) FROM autorizaciones"
                cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
    
    @staticmethod
    def get_observed_votes(connection: mysql.connector.MySQLConnection, departamento: Optional[str] = None) -> int:
        """Obtener votos observados pendientes"""
        cursor = connection.cursor()
        try:
            if departamento:
                query = """
                SELECT COUNT(v.id)
                FROM votos v
                JOIN circuitos c ON v.circuito_id = c.id
                JOIN establecimientos e ON c.establecimiento_id = e.id
                WHERE v.es_observado = TRUE AND v.estado_validacion = 'pendiente' AND e.departamento = %s
                """
                cursor.execute(query, (departamento,))
            else:
                query = """
                SELECT COUNT(id)
                FROM votos 
                WHERE es_observado = TRUE AND estado_validacion = 'pendiente'
                """
                cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
    
    @staticmethod
    def get_departments(connection: mysql.connector.MySQLConnection) -> List[Dict]:
        """Obtener lista de departamentos"""
        cursor = connection.cursor(dictionary=True)
        try:
            query = "SELECT DISTINCT departamento as nombre FROM establecimientos"
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    @staticmethod
    def get_circuit_results(connection: mysql.connector.MySQLConnection, circuito: str) -> Dict:
        """Obtener resultados por circuito específico"""
        cursor = connection.cursor(dictionary=True)
        try:
            # Información del circuito
            circuit_info_query = """
            SELECT c.numero_circuito, e.nombre as establecimiento, e.departamento, e.direccion
            FROM circuitos c
            JOIN establecimientos e ON c.establecimiento_id = e.id
            WHERE c.numero_circuito = %s
            """
            cursor.execute(circuit_info_query, (circuito,))
            circuit_info = cursor.fetchone()
            
            if not circuit_info:
                return None
            
            # Obtener la elección activa
            cursor.execute("SELECT id FROM elecciones WHERE activa = TRUE LIMIT 1")
            eleccion_activa = cursor.fetchone()
            
            if not eleccion_activa:
                return None
            
            # Votos por candidato en el circuito (solo presidenciales)
            votes_query = """
            SELECT ca.nombre as candidato, p.nombre as partido, COUNT(v.id) as votos
            FROM candidatos ca
            JOIN partidos p ON ca.partido_id = p.id
            LEFT JOIN votos v ON ca.id = v.candidato_id 
                AND v.estado_validacion = 'aprobado'
                AND v.circuito_id = (SELECT id FROM circuitos WHERE numero_circuito = %s)
            WHERE ca.es_presidente = TRUE AND ca.eleccion_id = %s
            GROUP BY ca.id, ca.nombre, p.nombre
            ORDER BY votos DESC
            """
            cursor.execute(votes_query, (circuito, eleccion_activa['id']))
            votos_candidatos = cursor.fetchall()
            
            # Votos en blanco (solo de la elección activa)
            blank_query = """
            SELECT COUNT(v.id) as votos_blanco
            FROM votos v
            JOIN circuitos c ON v.circuito_id = c.id
            WHERE c.numero_circuito = %s 
                AND v.candidato_id IS NULL 
                AND v.es_anulado = FALSE 
                AND v.estado_validacion = 'aprobado'
                AND v.timestamp >= (SELECT fecha_creacion FROM elecciones WHERE id = %s)
            """
            cursor.execute(blank_query, (circuito, eleccion_activa['id']))
            votos_blanco = cursor.fetchone()['votos_blanco'] or 0
            
            # Votos anulados (solo de la elección activa)
            nullified_query = """
            SELECT COUNT(v.id) as votos_anulados
            FROM votos v
            JOIN circuitos c ON v.circuito_id = c.id
            WHERE c.numero_circuito = %s 
                AND v.es_anulado = TRUE 
                AND v.estado_validacion = 'aprobado'
                AND v.timestamp >= (SELECT fecha_creacion FROM elecciones WHERE id = %s)
            """
            cursor.execute(nullified_query, (circuito, eleccion_activa['id']))
            votos_anulados = cursor.fetchone()['votos_anulados'] or 0
            
            # Total de votos (solo de la elección activa)
            total_query = """
            SELECT COUNT(v.id) as total_votos
            FROM votos v
            JOIN circuitos c ON v.circuito_id = c.id
            WHERE c.numero_circuito = %s 
                AND v.estado_validacion = 'aprobado'
                AND v.timestamp >= (SELECT fecha_creacion FROM elecciones WHERE id = %s)
            """
            cursor.execute(total_query, (circuito, eleccion_activa['id']))
            total_votos = cursor.fetchone()['total_votos'] or 0
            
            return {
                "circuito": circuit_info,
                "resultados": votos_candidatos,
                "votos_blanco": votos_blanco,
                "votos_anulados": votos_anulados,
                "total_votos": total_votos
            }
        finally:
            cursor.close()
            
    @staticmethod
    def search_circuits(connection: mysql.connector.MySQLConnection, search_term: str) -> List[Dict]:
        """Buscar circuitos por número"""
        cursor = connection.cursor(dictionary=True)
        try:
            # Si el término es "ALL", mostrar todos los circuitos disponibles
            if search_term.upper() == "ALL":
                query = """
                SELECT c.numero_circuito, e.nombre as establecimiento, e.departamento
                FROM circuitos c
                JOIN establecimientos e ON c.establecimiento_id = e.id
                ORDER BY CAST(c.numero_circuito AS UNSIGNED)
                """
                cursor.execute(query)
                resultados = cursor.fetchall()
                return resultados
            
            test_query = "SELECT COUNT(*) as total FROM circuitos"
            cursor.execute(test_query)
            total_circuits = cursor.fetchone()
            
            all_query = "SELECT numero_circuito FROM circuitos ORDER BY CAST(numero_circuito AS UNSIGNED)"
            cursor.execute(all_query)
            all_numbers = cursor.fetchall()
            números_disponibles = [item['numero_circuito'] for item in all_numbers]
            
            query = """
            SELECT c.numero_circuito, e.nombre as establecimiento, e.departamento
            FROM circuitos c
            JOIN establecimientos e ON c.establecimiento_id = e.id
            WHERE c.numero_circuito LIKE %s
            ORDER BY CAST(c.numero_circuito AS UNSIGNED)
            LIMIT 10
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern,))
            resultados = cursor.fetchall()
            return resultados
        except Exception as e:
            print(f"ERROR en búsqueda de circuitos: {e}")
            return []
        finally:
            cursor.close()