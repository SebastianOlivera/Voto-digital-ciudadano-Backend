from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CandidatoResponse(BaseModel):
    id: int
    nombre: str

class PartidoResponse(BaseModel):
    partido: str
    candidatos: List[CandidatoResponse]

class VotoRequest(BaseModel):
    cedula: str
    candidato_id: int

class VoteEnableRequest(BaseModel):
    credencial: str
    circuito: str
    esEspecial: Optional[bool] = False
    cedula_real: Optional[str] = None  # Para votos observados

class EstablecimientoInfo(BaseModel):
    id: int
    nombre: str
    departamento: str
    ciudad: str
    zona: Optional[str]
    barrio: Optional[str]
    direccion: str
    tipo_establecimiento: str
    accesible: bool

class CircuitoInfo(BaseModel):
    id: int
    numero_circuito: str
    establecimiento: EstablecimientoInfo

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    circuito: Optional[CircuitoInfo]
    username: str
    role: str

class VotoResponse(BaseModel):
    mensaje: str

class ResultadosResponse(BaseModel):
    resultados: List[dict]
    votos_blanco: int
    total_votos: int
    total_votantes: int
    participacion: float
    votos_observados: int
    mesas_cerradas: int
    total_mesas: int

class VotanteStatus(BaseModel):
    cedula: str
    estado: str
    autorizado_por: Optional[str] = None
    fecha_autorizacion: Optional[datetime] = None

class ValidarVotoRequest(BaseModel):
    voto_id: int
    accion: str  # "validar" o "rechazar"

class CerrarMesaRequest(BaseModel):
    circuito: str