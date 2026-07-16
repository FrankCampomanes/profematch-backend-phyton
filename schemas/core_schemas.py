from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProfesorUpdateProfile(BaseModel):
    descripcion: Optional[str] = None
    metodologia: Optional[str] = None
    reconocimientos: Optional[List[Any]] = []
    horarios: Optional[Dict[str, Any]] = {}
    cursos: Optional[List[str]] = []

class ResenaItem(BaseModel):
    estudiante: str
    comentario: str
    fecha: datetime
    puntuaciones: Dict[str, Any]

class MetricasProfesor(BaseModel):
    estudiantesAtendidos: int
    tasaAprobacion: str
    tiempoRespuesta: str

class ProfesorListResponse(BaseModel):
    id: int
    nombre: str
    email: str
    descripcion: Optional[str]
    metodologia: Optional[str]
    universidad: Optional[str]
    foto: Optional[str]
    perfil_completado: bool
    reconocimientos: List[Any]
    horarios: Dict[str, Any]
    cursos: List[str]
    rating: float
    criteriosEvaluacion: Dict[str, float]
    resenas: List[ResenaItem]
    metricas: MetricasProfesor

class SesionCreate(BaseModel):
    profesor_id: int
    curso_id: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    tema: str
    precio: int
    cupos_maximos: Optional[int] = 1
    enlace_reunion: Optional[str] = None
