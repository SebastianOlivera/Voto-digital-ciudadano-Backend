
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Esquemas de respuesta
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

class CandidatoResponse(BaseModel):
    id: int
    nombre: str
    orden_lista: Optional[int] = None

class PartidoResponse(BaseModel):
    partido: str
    candidatos: List[CandidatoResponse]

# Esquemas de request
class VoteEnableRequest(BaseModel):
    credencial: str
    circuito: str  # Agregar el campo circuito que faltaba
    cedula_real: Optional[str] = None
    esEspecial: bool = False

class VotanteStatus(BaseModel):
    cedula: str
    estado: str
    circuito_id: Optional[int] = None
    fecha_autorizacion: Optional[datetime] = None
    fecha_voto: Optional[datetime] = None
    es_autorizacion_especial: Optional[bool] = False

class VotoRequest(BaseModel):
    cedula: str
    candidato_id: int  # -1 = anulado, 0 = blanco, >0 = candidato

class VotoResponse(BaseModel):
    mensaje: str

class ValidarVotoRequest(BaseModel):
    voto_id: int
    accion: str  # "validar" o "rechazar"

class CerrarMesaRequest(BaseModel):
    circuito: str
