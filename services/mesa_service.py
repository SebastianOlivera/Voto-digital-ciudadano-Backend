def close_circuit(circuito: str) -> dict:
    """Cerrar circuito - compatibilidad"""
    return {"mensaje": f"Circuito {circuito} cerrado exitosamente"}

def close_mesa(circuito: str) -> dict:
    """Cerrar mesa"""
    return {"mensaje": f"Mesa del circuito {circuito} cerrada exitosamente"}