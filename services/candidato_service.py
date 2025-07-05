from typing import List, Dict
from database import get_db_connection
from dao.candidato_dao import CandidatoDAO
from schemas import PartidoResponse, CandidatoResponse

def get_candidates() -> List[PartidoResponse]:
    """Obtener todos los candidatos agrupados por partido de la elección activa"""
    with get_db_connection() as connection:
        # Primero obtener la elección activa
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM elecciones WHERE activa = TRUE LIMIT 1")
        eleccion_activa = cursor.fetchone()
        cursor.close()
        
        if not eleccion_activa:
            return []  # No hay elección activa
        
        candidatos = CandidatoDAO.get_all_with_parties_by_election(connection, eleccion_activa['id'])

        # Agrupar por partido y número de lista para combinar presidente y vicepresidente
        partidos_dict: Dict[str, Dict[int, Dict[str, any]]] = {}
        for candidato in candidatos:
            partido = candidato['partido_nombre']
            numero_lista = candidato.get('numero_lista')
            if partido not in partidos_dict:
                partidos_dict[partido] = {'color': candidato.get('partido_color')}
            if numero_lista not in partidos_dict[partido]:
                partidos_dict[partido][numero_lista] = {
                    'id': None,
                    'presidente': '',
                    'vicepresidente': ''
                }

            if candidato.get('es_presidente'):
                partidos_dict[partido][numero_lista]['id'] = candidato['id']
                partidos_dict[partido][numero_lista]['presidente'] = candidato['candidato_nombre']
            else:
                partidos_dict[partido][numero_lista]['vicepresidente'] = candidato['candidato_nombre']

        result: List[PartidoResponse] = []
        for partido, listas in partidos_dict.items():
            candidatos_list: List[CandidatoResponse] = []
            for numero_lista, datos in listas.items():
                nombre = datos['presidente']
                if datos['vicepresidente']:
                    nombre = f"{datos['presidente']} - {datos['vicepresidente']}"
                candidatos_list.append(
                    CandidatoResponse(
                        id=datos['id'],
                        nombre=nombre,
                        orden_lista=numero_lista
                    )
                )
            result.append(PartidoResponse(
                partido=partido, 
                candidatos=candidatos_list,
                color=listas.get('color')
            ))

        return result
