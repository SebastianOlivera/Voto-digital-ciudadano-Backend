from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(100))
    is_active = Column(Boolean, default=True)

class Partido(Base):
    __tablename__ = "partidos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True)
    candidatos = relationship("Candidato", back_populates="partido")

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    partido_id = Column(Integer, ForeignKey("partidos.id"))
    partido = relationship("Partido", back_populates="candidatos")

class Voto(Base):
    __tablename__ = "votos"
    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), index=True)
    candidato_id = Column(Integer, ForeignKey("candidatos.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    candidato = relationship("Candidato")
    
class Autorizacion(Base):
    __tablename__ = "autorizaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), index=True, nullable=False)  # Agregué longitud 20
    circuito = Column(String(10), nullable=False)  # Agregué longitud 10
    estado = Column(String(20), default='HABILITADA')  # Agregué longitud 20
    autorizado_por = Column(String(50), nullable=True)  # Agregué longitud 50
    fecha_autorizacion = Column(DateTime, default=datetime.utcnow)
    fecha_voto = Column(DateTime, nullable=True)