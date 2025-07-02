from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, database, auth
from pydantic import BaseModel
from dotenv import load_dotenv
import os

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

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class VotoResponse(BaseModel):
    mensaje: str

# Auth dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return auth.verify_token(token)

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
    partidos = db.query(models.Partido).all()
    return [PartidoResponse(partido=p.nombre, candidatos=[CandidatoResponse(id=c.id, nombre=c.nombre) for c in p.candidatos]) for p in partidos]

@app.post("/api/votar", response_model=VotoResponse)
async def votar(
    voto: VotoRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    existing_vote = db.query(models.Voto).filter(models.Voto.cedula == voto.cedula).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="Esta cédula ya ha votado")
    new_vote = models.Voto(cedula=voto.cedula, candidato_id=voto.candidato_id if voto.candidato_id > 0 else None)
    db.add(new_vote)
    db.commit()
    return VotoResponse(mensaje="Voto registrado exitosamente")

@app.get("/api/resultados")
async def get_resultados(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    from sqlalchemy import func
    resultados = db.query(
        models.Candidato.nombre.label("candidato"),
        models.Partido.nombre.label("partido"),
        func.count(models.Voto.id).label("votos")
    ).join(models.Voto, models.Candidato.id == models.Voto.candidato_id)     .join(models.Partido, models.Candidato.partido_id == models.Partido.id)     .group_by(models.Candidato.id).all()
    votos_blanco = db.query(func.count(models.Voto.id)).filter(models.Voto.candidato_id.is_(None)).scalar()
    total_votos = db.query(func.count(models.Voto.id)).scalar()
    return {"resultados": [{"candidato": r.candidato, "partido": r.partido, "votos": r.votos} for r in resultados], "votos_blanco": votos_blanco, "total_votos": total_votos}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
