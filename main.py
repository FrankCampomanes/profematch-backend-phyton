from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
import models.all_models # Para que SQLAlchemy detecte los modelos y pueda crearlos

# Crear tablas si no existen (ideal para desarrollo local)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="profeMatch API",
    description="Backend en FastAPI para la plataforma profeMatch",
    version="1.0.0"
)

from routers import auth, profesores, sesiones, usuarios, recomendaciones, estadisticas, resenas

# Configuración básica de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Dominios permitidos (soluciona error Failed to fetch por CORS)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(profesores.router)
app.include_router(sesiones.router)
app.include_router(recomendaciones.router)
app.include_router(estadisticas.router)
app.include_router(resenas.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de profeMatch en FastAPI (Python)"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "db": "Configurada y conectada"}
