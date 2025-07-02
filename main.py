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

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

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
    if not user or not auth.verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

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
    # Verificar si ya está autorizado
    existing_auth = db.query(models.Autorizacion).filter(
        models.Autorizacion.cedula == request.credencial
    ).first()
    
    if existing_auth:
        raise HTTPException(status_code=400, detail="Votante ya autorizado")
    
    # Crear nueva autorización
    nueva_auth = models.Autorizacion(
        cedula=request.credencial,
        circuito=request.circuito,
        estado='HABILITADA',
        autorizado_por=current_user,
        fecha_autorizacion=datetime.now()
    )
    db.add(nueva_auth)
    db.commit()
    
    return {"mensaje": f"Votante {request.credencial} autorizado exitosamente"}

@app.get("/api/votante/{circuito}/{cedula}", response_model=VotanteStatus)
async def get_votante(
    circuito: str,
    cedula: str,
    db: Session = Depends(database.get_db)
):
    """Verificar estado de votante - no requiere auth para cabina"""
    auth_record = db.query(models.Autorizacion).filter(
        models.Autorizacion.cedula == cedula,
        models.Autorizacion.circuito == circuito
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
    db: Session = Depends(database.get_db)
):
    """Votar - no requiere auth individual, se verifica autorización previa"""
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
    
    # Registrar voto
    new_vote = models.Voto(
        cedula=voto.cedula, 
        candidato_id=voto.candidato_id if voto.candidato_id > 0 else None,
        fecha_hora=datetime.now(),
        estado='VÁLIDO'
    )
    db.add(new_vote)
    
    # Actualizar estado de autorización
    auth_record.estado = 'VOTÓ'
    auth_record.fecha_voto = datetime.now()
    
    db.commit()
    return VotoResponse(mensaje="Voto registrado exitosamente")

@app.get("/api/resultados", response_model=ResultadosResponse)
async def get_resultados(db: Session = Depends(database.get_db)):
    """Resultados públicos - no requiere autenticación"""
    from sqlalchemy import func
    
    # Resultados por candidato
    resultados = db.query(
        models.Candidato.nombre.label("candidato"),
        models.Partido.nombre.label("partido"),
        func.count(models.Voto.id).label("votos")
    ).join(models.Voto, models.Candidato.id == models.Voto.candidato_id, isouter=True) \
     .join(models.Partido, models.Candidato.partido_id == models.Partido.id) \
     .group_by(models.Candidato.id).all()
    
    # Votos en blanco
    votos_blanco = db.query(func.count(models.Voto.id)).filter(models.Voto.candidato_id.is_(None)).scalar() or 0
    
    # Total de votos
    total_votos = db.query(func.count(models.Voto.id)).scalar() or 0
    
    # Estadísticas adicionales
    total_votantes = db.query(func.count(models.Autorizacion.id)).scalar() or 0
    participacion = (total_votos / total_votantes * 100) if total_votantes > 0 else 0
    votos_observados = 0  # Implementar lógica si necesario
    mesas_cerradas = 0    # Implementar lógica si necesario  
    total_mesas = 1       # Ajustar según tu lógica
    
    return ResultadosResponse(
        resultados=[{"candidato": r.candidato, "partido": r.partido, "votos": r.votos} for r in resultados],
        votos_blanco=votos_blanco,
        total_votos=total_votos,
        total_votantes=total_votantes,
        participacion=round(participacion, 1),
        votos_observados=votos_observados,
        mesas_cerradas=mesas_cerradas,
        total_mesas=total_mesas
    )

# Endpoints adicionales para administración (requieren auth)
@app.get("/api/votantes/{circuito}")
async def get_votantes_por_circuito(
    circuito: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Listar votantes por circuito - solo para mesa autenticada"""
    votantes = db.query(models.Autorizacion).filter(
        models.Autorizacion.circuito == circuito
    ).all()
    return [{"cedula": v.cedula, "estado": v.estado, "fecha_autorizacion": v.fecha_autorizacion} for v in votantes]

@app.patch("/api/circuito/{circuito}/close")
async def close_circuito(
    circuito: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Cerrar circuito - solo para mesa autenticada"""
    # Implementar lógica de cierre
    return {"mensaje": f"Circuito {circuito} cerrado exitosamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)