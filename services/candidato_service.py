from typing import List
from database import get_db_connection
from dao.candidato_dao import CandidatoDAO
from schemas import PartidoResponse, CandidatoResponse

def get_candidates() -> List[PartidoResponse]:
    """Obtener todos los candidatos agrupados por partido"""
    with get_db_connection() as connection:
        candidatos = CandidatoDAO.get_all_with_parties(connection)
        
        # Agrupar candidatos por partido
        partidos_dict = {}
        for candidato in candidatos:
            partido_nombre = candidato['partido_nombre']
            if partido_nombre not in partidos_dict:
                partidos_dict[partido_nombre] = []
            partidos_dict[partido_nombre].append(CandidatoResponse(
                id=candidato['id'],
                nombre=candidato['candidato_nombre'],
                orden_lista=candidato.get('orden_lista')
            ))
        
        return [
            PartidoResponse(partido=partido, candidatos=candidatos_list)
            for partido, candidatos_list in partidos_dict.items()
        ]