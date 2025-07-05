
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
    color: Optional[str] = None

# Esquemas de request
class VoteEnableRequest(BaseModel):
    credencial: str
    circuito: str  # Agregar el campo circuito que faltaba
    credencial_civica: Optional[str] = None
    esEspecial: bool = False

class VotanteStatus(BaseModel):
    credencial: str
    estado: str
    circuito_id: Optional[int] = None
    fecha_autorizacion: Optional[datetime] = None
    fecha_voto: Optional[datetime] = None
    es_autorizacion_especial: Optional[bool] = False

class VotoRequest(BaseModel):
    credencial: str
    candidato_id: int  # -1 = anulado, 0 = blanco, >0 = candidato

class VotoResponse(BaseModel):
    mensaje: str

class ValidarVotoRequest(BaseModel):
    voto_id: int
    accion: str  # "validar" o "rechazar"

class CerrarMesaRequest(BaseModel):
    circuito: str

# Esquemas para crear entidades
class CreateUsuarioRequest(BaseModel):
    username: str
    password: str
    circuito_id: int
    role: str  # "mesa" o "presidente"

class CreateEstablecimientoRequest(BaseModel):
    nombre: str
    departamento: str
    ciudad: str
    zona: Optional[str] = None
    barrio: Optional[str] = None
    direccion: str
    tipo_establecimiento: str
    accesible: bool = True

class CreateEleccionRequest(BaseModel):
    año: int
    listas: List['CreateListaRequest']

class CreateListaRequest(BaseModel):
    candidato: str
    vicepresidente: str
    numero_lista: int
    partido_id: int

class CreatePartidoRequest(BaseModel):
    nombre: str
    color: str  # Formato hex como #FF0000

class CreateCircuitoRequest(BaseModel):
    numero_circuito: str
    numero_mesa: str
    establecimiento_id: int

# Response schemas
class UsuarioCreatedResponse(BaseModel):
    id: int
    username: str
    circuito_id: int
    role: str
    mensaje: str

class PartidoCreatedResponse(BaseModel):
    id: int
    nombre: str
    color: str
    mensaje: str

class EstablecimientoCreatedResponse(BaseModel):
    id: int
    nombre: str
    departamento: str
    mensaje: str
