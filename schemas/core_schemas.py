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
    id: int
    estudiante: str
    comentario: str
    fecha: datetime
    puntuaciones: Dict[str, Any]
    estrellas_calculadas: float
    respuesta_profesor: Optional[str] = None

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
    cursos: List[Dict[str, Any]]
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
class SesionOut(BaseModel):
    id: int
    tema: str
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: str
    cupos_maximos: int
    inscritos_actuales: int
    precio: int
    enlace_reunion: Optional[str] = None
    profesor_id: int
    profesor_nombre: str
    curso_nombre: str

class InscribirRequest(BaseModel):
    estudiante_id: int

class InscripcionOut(BaseModel):
    inscripcion_id: int
    sesion_id: int
    tema: str
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado_sesion: str
    estado_inscripcion: str
    precio: int
    enlace_reunion: Optional[str] = None
    profesor_id: int
    profesor_nombre: str
    curso_nombre: str

class InscritoOut(BaseModel):
    estudiante_id: int
    nombre_estudiante: str
    estado_inscripcion: str

class ResenaCreate(BaseModel):
    estudiante_id: int
    profesor_id: int
    sesion_id: int
    puntuaciones_json: Dict[str, float]
    comentario: str
    recomendaria: bool
    queja_formal: bool
    motivo_queja: Optional[str] = None

class ResenaEstudianteOut(BaseModel):
    id: int
    profesor_id: int
    profesor_nombre: str
    sesion_id: int
    curso_nombre: str
    puntuaciones_json: Dict[str, float]
    comentario: str
    recomendaria: bool
    queja_formal: bool
    motivo_queja: Optional[str] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True
