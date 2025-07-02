from fastapi import APIRouter
from typing import Optional
from services.resultado_service import get_results, get_departments, get_circuit_results, search_circuits

router = APIRouter()

@router.get("/")
async def get_resultados(departamento: Optional[str] = None):
    """Resultados públicos - no requiere autenticación"""
    return get_results(departamento)

@router.get("/departamentos")
async def get_departamentos():
    """Obtener lista de departamentos disponibles"""
    return get_departments()

@router.get("/circuito/{numero_circuito}")
async def get_resultados_circuito(numero_circuito: str):
    """Obtener resultados por circuito específico"""
    return get_circuit_results(numero_circuito)

@router.get("/circuitos/buscar")
async def buscar_circuitos(q: str):
    """Buscar circuitos por número"""
    return search_circuits(q)