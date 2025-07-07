from database import get_db_connection, get_db_transaction
from dao.admin_dao import AdminDAO
from schemas import CreateUsuarioRequest, CreateEstablecimientoRequest, CreateEleccionRequest, CreateCircuitoRequest, CreatePartidoRequest
from fastapi import HTTPException

def create_usuario(data: CreateUsuarioRequest) -> dict:
    """Crear nuevo usuario (mesa o presidente)"""
    try:
        with get_db_connection() as connection:
            # Verificar que el rol sea válido
            if data.role not in ['mesa', 'presidente']:
                return {"error": "Rol inválido. Debe ser 'mesa' o 'presidente'"}
            
            # Verificar que el username no exista
            if AdminDAO.username_exists(connection, data.username):
                return {"error": f"El username '{data.username}' ya existe"}
            
            # Verificar que el circuito existe
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM circuitos WHERE id = %s", (data.circuito_id,))
            if not cursor.fetchone():
                cursor.close()
                return {"error": f"El circuito ID {data.circuito_id} no existe"}
            cursor.close()
            
            usuario_id = AdminDAO.create_usuario(connection, data.dict())
            connection.commit()
            
            return {
                "id": usuario_id,
                "username": data.username,
                "circuito_id": data.circuito_id,
                "role": data.role,
                "mensaje": f"Usuario {data.username} creado exitosamente"
            }
            
    except Exception as e:
        print(f"Error creando usuario: {e}")
        return {"error": f"Error creando usuario: {str(e)}"}

def create_establecimiento(data: CreateEstablecimientoRequest) -> dict:
    """Crear nuevo establecimiento"""
    try:
        with get_db_connection() as connection:
            establecimiento_id = AdminDAO.create_establecimiento(connection, data.dict())
            connection.commit()
            
            return {
                "id": establecimiento_id,
                "nombre": data.nombre,
                "departamento": data.departamento,
                "mensaje": f"Establecimiento '{data.nombre}' creado exitosamente"
            }
            
    except Exception as e:
        print(f"Error creando establecimiento: {e}")
        return {"error": f"Error creando establecimiento: {str(e)}"}

def create_eleccion(data: CreateEleccionRequest) -> dict:
    """Crear nueva elección con listas - FULL WIPE del sistema"""
    try:
        with get_db_connection() as connection:
            print(f"🧹 Iniciando FULL WIPE para crear elección {data.año}")
            
            success = AdminDAO.create_eleccion(connection, data.dict())
            if success:
                connection.commit()
                return {"mensaje": f"Elección {data.año} creada exitosamente con {len(data.listas)} listas (sistema limpiado completamente)"}
            else:
                connection.rollback()
                return {"error": "Error creando la elección"}
            
    except Exception as e:
        print(f"Error creando elección: {e}")
        return {"error": f"Error creando elección: {str(e)}"}

def create_circuito(data: CreateCircuitoRequest) -> dict:
    """Crear nuevo circuito"""
    try:
        with get_db_connection() as connection:
            # Verificar que el número de circuito no exista
            if AdminDAO.circuito_exists(connection, data.numero_circuito):
                return {"error": f"El circuito '{data.numero_circuito}' ya existe"}
            
            # Verificar que el establecimiento existe
            cursor = connection.cursor()
            cursor.execute("SELECT id, nombre FROM establecimientos WHERE id = %s", (data.establecimiento_id,))
            establecimiento = cursor.fetchone()
            cursor.close()
            
            if not establecimiento:
                return {"error": f"El establecimiento ID {data.establecimiento_id} no existe"}
            
            circuito_id = AdminDAO.create_circuito(connection, data.dict())
            connection.commit()
            
            return {
                "id": circuito_id,
                "numero_circuito": data.numero_circuito,
                "establecimiento": establecimiento[1],
                "mensaje": f"Circuito {data.numero_circuito} creado exitosamente"
            }
            
    except Exception as e:
        print(f"Error creando circuito: {e}")
        return {"error": f"Error creando circuito: {str(e)}"}

def get_establecimientos() -> list:
    """Obtener lista de establecimientos"""
    try:
        with get_db_connection() as connection:
            return AdminDAO.get_establecimientos_list(connection)
    except Exception as e:
        print(f"Error obteniendo establecimientos: {e}")
        return []

def get_circuitos() -> list:
    """Obtener lista de circuitos con sus IDs reales"""
    try:
        print("🔍 Obteniendo lista de circuitos...")
        with get_db_connection() as connection:
            result = AdminDAO.get_circuitos_list(connection)
            return result
    except Exception as e:
        print(f"Error obteniendo circuitos: {e}")
        return []

def create_partido(data: CreatePartidoRequest) -> dict:
    """Crear nuevo partido"""
    try:
        with get_db_transaction() as connection:
            partido = AdminDAO.create_partido(connection, data.dict())
            return {
                "id": partido["id"],
                "nombre": partido["nombre"],
                "mensaje": f"Partido '{partido['nombre']}' creado exitosamente"
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando partido: {str(e)}")

def get_partidos() -> list:
    """Obtener lista de partidos"""
    try:
        with get_db_connection() as connection:
            return AdminDAO.get_partidos_list(connection)
    except Exception as e:
        print(f"Error obteniendo partidos: {e}")
        return []