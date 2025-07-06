from fastapi import APIRouter
from database import get_db_connection

router = APIRouter()

@router.get("/activa")
async def get_eleccion_activa():
    """Obtener información de la elección activa"""
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT año, nombre, fecha_creacion FROM elecciones WHERE activa = TRUE LIMIT 1")
            eleccion = cursor.fetchone()
            if eleccion:
                return {
                    "año": eleccion["año"],
                    "nombre": eleccion["nombre"],
                    "fecha_creacion": eleccion["fecha_creacion"].isoformat() if eleccion["fecha_creacion"] else None
                }
            return {"año": 2024, "nombre": "Elección 2024", "fecha_creacion": None}
        finally:
            cursor.close()