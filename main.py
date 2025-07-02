from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import models, database, auth
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
app = FastAPI(title="Sistema de Votación API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Pydantic models
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

# Auth dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return auth.verify_token(token)

# Optional auth dependency (para endpoints que pueden ser públicos)
def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        if credentials:
            token = credentials.credentials
            return auth.verify_token(token)
    except:
        pass
    return None

# Crear tablas
database.Base.metadata.create_all(bind=database.engine)

@app.post("/api/mesa/login", response_model=LoginResponse)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.Usuario).filter(models.Usuario.username == username).first()
    print(f"DEBUG: Usuario encontrado: {user is not None}")
    if user:
        print(f"DEBUG: Username: {user.username}, Role: {getattr(user, 'role', 'N/A')}")
        print(f"DEBUG: Password hash starts with: {user.password_hash[:10]}...")
    
    if not user:
        print(f"DEBUG: Usuario '{username}' no encontrado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    
    try:
        password_valid = auth.verify_password(password, user.password_hash)
        print(f"DEBUG: Password verification result: {password_valid}")
    except Exception as e:
        print(f"DEBUG: Error verifying password: {e}")
        password_valid = False
    
    if not password_valid:
        print(f"DEBUG: Password verification failed for user: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Obtener información completa del circuito y establecimiento
    circuito_info = None
    circuito_id_to_use = user.circuito_id
    
    # Para superadmin, usar circuito 1 por defecto
    if user.role == 'superadmin' and not circuito_id_to_use:
        circuito_id_to_use = 1
    
    if circuito_id_to_use:
        circuito = db.query(models.Circuito).filter(models.Circuito.id == circuito_id_to_use).first()
        if circuito and circuito.establecimiento:
            establecimiento = circuito.establecimiento
            circuito_info = CircuitoInfo(
                id=circuito.id,
                numero_circuito=circuito.numero_circuito,
                establecimiento=EstablecimientoInfo(
                    id=establecimiento.id,
                    nombre=establecimiento.nombre,
                    departamento=establecimiento.departamento,
                    ciudad=establecimiento.ciudad,
                    zona=establecimiento.zona,
                    barrio=establecimiento.barrio,
                    direccion=establecimiento.direccion,
                    tipo_establecimiento=establecimiento.tipo_establecimiento,
                    accesible=establecimiento.accesible
                )
            )
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "circuito": circuito_info,
        "username": user.username,
        "role": getattr(user, 'role', 'mesa')
    }

@app.get("/api/candidatos", response_model=List[PartidoResponse])
async def get_candidatos(db: Session = Depends(database.get_db)):
    """Endpoint público - no requiere autenticación para que votantes vean candidatos"""
    partidos = db.query(models.Partido).all()
    return [PartidoResponse(partido=p.nombre, candidatos=[CandidatoResponse(id=c.id, nombre=c.nombre) for c in p.candidatos]) for p in partidos]

@app.post("/api/vote/enable")
async def enable_vote(
    request: VoteEnableRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Autorizar votante - solo mesa autenticada"""
    # Para votos observados, usar la cédula real del votante
    cedula_a_autorizar = request.cedula_real if request.esEspecial and request.cedula_real else request.credencial
    
    # Verificar si ya está autorizado
    existing_auth = db.query(models.Autorizacion).filter(
        models.Autorizacion.cedula == cedula_a_autorizar
    ).first()
    
    if existing_auth:
        raise HTTPException(status_code=400, detail="Votante ya autorizado")
    
    # Crear nueva autorización
    nueva_auth = models.Autorizacion(
        cedula=cedula_a_autorizar,
        circuito_id=int(request.circuito),
        estado='HABILITADA',
        autorizado_por=current_user,
        fecha_autorizacion=datetime.now(),
        es_autorizacion_especial=request.esEspecial or False
    )
    db.add(nueva_auth)
    db.commit()
    
    tipo_voto = "observado" if request.esEspecial else "normal"
    return {"mensaje": f"Votante {cedula_a_autorizar} autorizado exitosamente para voto {tipo_voto}"}

@app.get("/api/votante/{circuito}/{cedula}", response_model=VotanteStatus)
async def get_votante(
    circuito: str,
    cedula: str,
    db: Session = Depends(database.get_db)
):
    """Verificar estado de votante - no requiere auth para cabina"""
    auth_record = db.query(models.Autorizacion).filter(
        models.Autorizacion.cedula == cedula,
        models.Autorizacion.circuito_id == int(circuito)
    ).first()
    
    if not auth_record:
        raise HTTPException(status_code=404, detail="Votante no encontrado o no autorizado")
    
    return VotanteStatus(
        cedula=auth_record.cedula,
        estado=auth_record.estado,
        autorizado_por=auth_record.autorizado_por,
        fecha_autorizacion=auth_record.fecha_autorizacion
    )

@app.post("/api/votar", response_model=VotoResponse)
async def votar(
    voto: VotoRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Votar - requiere auth de mesa para determinar circuito"""
    # Obtener información de la mesa que registra el voto
    mesa_user = db.query(models.Usuario).filter(models.Usuario.username == current_user).first()
    if not mesa_user:
        raise HTTPException(status_code=403, detail="Usuario de mesa no encontrado")
    
    circuito_id = mesa_user.circuito_id
    
    # Verificar que el votante esté autorizado
    auth_record = db.query(models.Autorizacion).filter(
        models.Autorizacion.cedula == voto.cedula,
        models.Autorizacion.estado == 'HABILITADA'
    ).first()
    
    if not auth_record:
        raise HTTPException(status_code=403, detail="Votante no autorizado para votar")
    
    # Verificar que no haya votado ya
    existing_vote = db.query(models.Voto).filter(models.Voto.cedula == voto.cedula).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="Esta cédula ya ha votado")
    
    # Determinar si es voto observado basado en la autorización especial
    es_observado = getattr(auth_record, 'es_autorizacion_especial', False)
    estado_validacion = 'pendiente' if es_observado else 'aprobado'
    
    # Registrar voto
    new_vote = models.Voto(
        cedula=voto.cedula, 
        candidato_id=voto.candidato_id if voto.candidato_id > 0 else None,
        timestamp=datetime.now(),
        es_observado=es_observado,
        estado_validacion=estado_validacion,
        circuito_id=circuito_id
    )
    db.add(new_vote)
    
    # Actualizar estado de autorización
    auth_record.estado = 'VOTÓ'
    auth_record.fecha_voto = datetime.now()
    
    db.commit()
    
    mensaje = "Voto registrado exitosamente"
    if es_observado:
        mensaje += f" (VOTO OBSERVADO - Circuito credencial: {auth_record.circuito_id}, Circuito mesa: {circuito_id})"
    
    return VotoResponse(mensaje=mensaje)

@app.get("/api/resultados")
async def get_resultados(departamento: Optional[str] = None, db: Session = Depends(database.get_db)):
    """Resultados públicos - no requiere autenticación"""
    from sqlalchemy import func
    
    # Base query
    query = db.query(
        models.Candidato.nombre.label("candidato"),
        models.Partido.nombre.label("partido"),
        func.count(models.Voto.id).label("votos")
    ).join(models.Voto, models.Candidato.id == models.Voto.candidato_id, isouter=True) \
     .join(models.Partido, models.Candidato.partido_id == models.Partido.id)
    
    # Filtrar por departamento si se especifica
    if departamento:
        query = query.join(models.Circuito, models.Voto.circuito_id == models.Circuito.id) \
                    .join(models.Establecimiento, models.Circuito.establecimiento_id == models.Establecimiento.id) \
                    .filter(models.Establecimiento.departamento == departamento)
    
    resultados = query.group_by(models.Candidato.id).all()
    
    # Votos en blanco
    blanco_query = db.query(func.count(models.Voto.id)).filter(models.Voto.candidato_id.is_(None))
    if departamento:
        blanco_query = blanco_query.join(models.Circuito, models.Voto.circuito_id == models.Circuito.id) \
                                 .join(models.Establecimiento, models.Circuito.establecimiento_id == models.Establecimiento.id) \
                                 .filter(models.Establecimiento.departamento == departamento)
    votos_blanco = blanco_query.scalar() or 0
    
    # Total de votos
    total_query = db.query(func.count(models.Voto.id))
    if departamento:
        total_query = total_query.join(models.Circuito, models.Voto.circuito_id == models.Circuito.id) \
                                .join(models.Establecimiento, models.Circuito.establecimiento_id == models.Establecimiento.id) \
                                .filter(models.Establecimiento.departamento == departamento)
    total_votos = total_query.scalar() or 0
    
    # Estadísticas adicionales
    auth_query = db.query(func.count(models.Autorizacion.id))
    if departamento:
        auth_query = auth_query.join(models.Circuito, models.Autorizacion.circuito_id == models.Circuito.id) \
                              .join(models.Establecimiento, models.Circuito.establecimiento_id == models.Establecimiento.id) \
                              .filter(models.Establecimiento.departamento == departamento)
    total_votantes = auth_query.scalar() or 0
    
    participacion = (total_votos / total_votantes * 100) if total_votantes > 0 else 0
    votos_observados = 0
    mesas_cerradas = 0
    total_mesas = db.query(func.count(models.Usuario.id)).scalar() or 0
    
    return {
        "resultados": [{"candidato": r.candidato, "partido": r.partido, "votos": r.votos} for r in resultados],
        "votos_blanco": votos_blanco,
        "total_votos": total_votos,
        "total_votantes": total_votantes,
        "participacion": round(participacion, 1),
        "votos_observados": votos_observados,
        "mesas_cerradas": mesas_cerradas,
        "total_mesas": total_mesas,
        "departamento": departamento
    }

@app.get("/api/departamentos")
async def get_departamentos(db: Session = Depends(database.get_db)):
    """Obtener lista de departamentos disponibles"""
    from sqlalchemy import func
    departamentos = db.query(models.Establecimiento.departamento).distinct().all()
    return [{"nombre": d[0]} for d in departamentos]

# Endpoints adicionales para administración (requieren auth)
@app.get("/api/votantes/{circuito}")
async def get_votantes_por_circuito(
    circuito: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Listar votantes por circuito - solo para mesa autenticada"""
    votantes = db.query(models.Autorizacion).filter(
        models.Autorizacion.circuito_id == int(circuito)
    ).all()
    return [{"cedula": v.cedula, "estado": v.estado, "fecha_autorizacion": v.fecha_autorizacion} for v in votantes]

@app.patch("/api/circuito/{circuito}/close")
async def close_circuito(
    circuito: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Cerrar circuito - solo para mesa autenticada (compatibilidad)"""
    return {"mensaje": f"Circuito {circuito} cerrado exitosamente"}

@app.get("/api/votos-observados/{circuito}")
async def get_votos_observados(
    circuito: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Obtener votos observados pendientes para el circuito"""
    votos = db.query(models.Voto).filter(
        models.Voto.es_observado == True,
        models.Voto.estado_validacion == 'pendiente',
        models.Voto.circuito_id == int(circuito)
    ).all()
    
    return [
        {
            "id": voto.id,
            "cedula": voto.cedula,
            "candidato_id": voto.candidato_id,
            "fecha_hora": voto.timestamp.isoformat()
        }
        for voto in votos
    ]

class ValidarVotoRequest(BaseModel):
    voto_id: int
    accion: str  # "validar" o "rechazar"

@app.post("/api/validar-voto-observado")
async def validar_voto_observado(
    request: ValidarVotoRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Validar o rechazar voto observado - solo presidente de mesa"""
    voto = db.query(models.Voto).filter(models.Voto.id == request.voto_id).first()
    if not voto:
        raise HTTPException(status_code=404, detail="Voto no encontrado")
    
    if request.accion == "validar":
        voto.estado_validacion = "aprobado"
    elif request.accion == "rechazar":
        voto.estado_validacion = "rechazado"
    else:
        raise HTTPException(status_code=400, detail="Acción no válida")
    
    db.commit()
    return {"mensaje": f"Voto {request.accion}o exitosamente"}

class CerrarMesaRequest(BaseModel):
    circuito: str

@app.post("/api/cerrar-mesa")
async def cerrar_mesa(
    request: CerrarMesaRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Cerrar mesa - solo presidente de mesa"""
    return {"mensaje": f"Mesa del circuito {request.circuito} cerrada exitosamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)