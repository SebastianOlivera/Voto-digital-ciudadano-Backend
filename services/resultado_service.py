from typing import Optional
from database import get_db_connection
from dao.resultado_dao import ResultadoDAO

def get_results(departamento: Optional[str] = None) -> dict:
    """Obtener resultados de votación"""
    with get_db_connection() as connection:
        # Obtener información de la elección activa
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT año FROM elecciones WHERE activa = TRUE LIMIT 1")
        eleccion_activa = cursor.fetchone()
        cursor.close()
        
        año_eleccion = eleccion_activa['año'] if eleccion_activa else 2024
        
        # Obtener votos por candidato
        resultados_raw = ResultadoDAO.get_votes_by_candidate(connection, departamento)
        resultados = [{"candidato": r["candidato"], "partido": r["partido"], "votos": r["votos"]} for r in resultados_raw]
        
        # Obtener estadísticas
        votos_blanco = ResultadoDAO.get_blank_votes(connection, departamento)
        votos_anulados = ResultadoDAO.get_nullified_votes(connection, departamento)
        total_votos = ResultadoDAO.get_total_votes(connection, departamento)
        total_votantes = ResultadoDAO.get_total_voters(connection, departamento)
        votos_observados = ResultadoDAO.get_observed_votes(connection, departamento)
        
        participacion = (total_votos / total_votantes * 100) if total_votantes > 0 else 0
        mesas_cerradas = 0
        total_mesas = 0  # TODO: implementar en DAO si es necesario
    
        return {
            "resultados": resultados,
            "votos_blanco": votos_blanco,
            "votos_anulados": votos_anulados,
            "total_votos": total_votos,
            "total_votantes": total_votantes,
            "participacion": round(participacion, 1),
            "votos_observados": votos_observados,
            "mesas_cerradas": mesas_cerradas,
            "total_mesas": total_mesas,
            "departamento": departamento,
            "año_eleccion": año_eleccion
        }

def get_departments() -> list:
    """Obtener lista de departamentos disponibles"""
    with get_db_connection() as connection:
        return ResultadoDAO.get_departments(connection)

def get_circuit_results(circuito: str) -> dict:
    """Obtener resultados por circuito"""
    with get_db_connection() as connection:
        result = ResultadoDAO.get_circuit_results(connection, circuito)
        if not result:
            return {"error": "Circuito no encontrado"}
        return result

def search_circuits(search_term: str) -> list:
    """Buscar circuitos por número"""
    print(f"🔍 Servicio: Buscando circuitos con término: '{search_term}'")
    with get_db_connection() as connection:
        result = ResultadoDAO.search_circuits(connection, search_term)
        print(f"🔍 Servicio: Resultado obtenido: {result}")
        return result