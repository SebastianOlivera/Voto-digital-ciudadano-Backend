from database import get_db_connection
from dao.mesa_dao import MesaDAO

def close_circuit(circuito: str) -> dict:
    """Cerrar circuito efectivamente"""
    try:
        print(f"🔒 Cerrando circuito {circuito}...")
        with get_db_connection() as connection:
            # Obtener circuito_id desde número de circuito
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM circuitos WHERE numero_circuito = %s", (circuito,))
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return {"error": f"Circuito {circuito} no encontrado"}
            
            circuito_id = result[0]
            success = MesaDAO.close_mesa(connection, circuito_id)
            
            if success:
                connection.commit()
                print(f"✅ Circuito {circuito} cerrado exitosamente")
                return {"mensaje": f"Circuito {circuito} cerrado exitosamente"}
            else:
                return {"error": f"No se pudo cerrar el circuito {circuito}"}
                
    except Exception as e:
        print(f"❌ Error cerrando circuito {circuito}: {e}")
        return {"error": f"Error cerrando circuito: {str(e)}"}

def close_mesa(circuito: str) -> dict:
    """Cerrar mesa - delega a close_circuit para mantener compatibilidad"""
    return close_circuit(circuito)

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