from database import get_db_connection
from dao.mesa_dao import MesaDAO

def close_circuit(circuito: str) -> dict:
    """Cerrar circuito - compatibilidad"""
    return {"mensaje": f"Circuito {circuito} cerrado exitosamente"}

def close_mesa(circuito: str) -> dict:
    """Cerrar mesa"""
    return {"mensaje": f"Mesa del circuito {circuito} cerrada exitosamente"}

def get_mesas_estado() -> list:
    """Obtener estado de todas las mesas"""
    try:
        print("🔍 Obteniendo estado de mesas...")
        with get_db_connection() as connection:
            result = MesaDAO.get_all_mesas_estado(connection)
            print(f"✅ Estado de mesas obtenido: {len(result)} mesas encontradas")
            return result
    except Exception as e:
        print(f"❌ Error en get_mesas_estado: {e}")
        return []