from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Establecimiento(Base):
    __tablename__ = "establecimientos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    departamento = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=False)
    zona = Column(String(100), nullable=True)
    barrio = Column(String(100), nullable=True)
    direccion = Column(String(300), nullable=False)
    tipo_establecimiento = Column(String(50), nullable=False)  # escuela, liceo, universidad, etc.
    accesible = Column(Boolean, default=False)
    circuitos = relationship("Circuito", back_populates="establecimiento")

class Circuito(Base):
    __tablename__ = "circuitos"
    id = Column(Integer, primary_key=True, index=True)
    numero_circuito = Column(String(10), unique=True, nullable=False, index=True)
    numero_mesa = Column(String(10), nullable=False)  # Mesa integrada al circuito (1:1)
    establecimiento_id = Column(Integer, ForeignKey("establecimientos.id"))
    establecimiento = relationship("Establecimiento", back_populates="circuitos")
    usuarios = relationship("Usuario", back_populates="circuito")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(100))
    is_active = Column(Boolean, default=True)
    circuito_id = Column(Integer, ForeignKey("circuitos.id"), nullable=True)
    role = Column(String(20), default="mesa")
    circuito = relationship("Circuito", back_populates="usuarios")

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
    es_observado = Column(Boolean, default=False)
    estado_validacion = Column(String(20), default='aprobado')  # 'aprobado', 'pendiente', 'rechazado'
    circuito_id = Column(Integer, ForeignKey("circuitos.id"), nullable=True)  # Circuito donde se emitió el voto
    es_anulado = Column(Boolean, default=False)  # Para distinguir votos anulados de votos en blanco
    candidato = relationship("Candidato")
    
class Autorizacion(Base):
    __tablename__ = "autorizaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), index=True, nullable=False)  # Agregué longitud 20
    circuito_id = Column(Integer, ForeignKey("circuitos.id"), nullable=False)
    estado = Column(String(20), default='HABILITADA')  # Agregué longitud 20
    autorizado_por = Column(String(50), nullable=True)  # Agregué longitud 50
    fecha_autorizacion = Column(DateTime, default=datetime.utcnow)
    fecha_voto = Column(DateTime, nullable=True)
    es_autorizacion_especial = Column(Boolean, default=False)  # Para votos observados