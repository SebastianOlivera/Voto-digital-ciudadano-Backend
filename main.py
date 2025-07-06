from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import init_connection_pool
from routers import auth, votante, voto, candidato, resultado, mesa, credencial, admin, eleccion

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

# Inicializar pool de conexiones
init_connection_pool()

# Incluir routers
app.include_router(auth.router, prefix="/api/mesa", tags=["auth"])
app.include_router(votante.router, prefix="/api/votantes", tags=["votante"])
app.include_router(voto.router, prefix="/api", tags=["voto"])
app.include_router(candidato.router, prefix="/api/candidatos", tags=["candidato"])
app.include_router(resultado.router, prefix="/api/resultados", tags=["resultado"])
app.include_router(mesa.router, prefix="/api/circuito", tags=["mesa"])
app.include_router(credencial.router, prefix="/api/credenciales", tags=["credenciales"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(eleccion.router, prefix="/api/eleccion", tags=["eleccion"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)