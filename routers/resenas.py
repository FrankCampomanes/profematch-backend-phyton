from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel
import json

from core.database import get_db
from models.all_models import Resena, Sesion, Usuario
from schemas.core_schemas import ResenaCreate, ResenaEstudianteOut

router = APIRouter(prefix="/api/resenas", tags=["Reseñas"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_resena(resena: ResenaCreate, db: Session = Depends(get_db)):
    # Validar sesión
    sesion = db.query(Sesion).filter(Sesion.id == resena.sesion_id).first()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
    # Crear reseña
    nueva_resena = Resena(
        profesor_id=resena.profesor_id,
        estudiante_id=resena.estudiante_id,
        sesion_id=resena.sesion_id,
        puntuaciones_json=json.dumps(resena.puntuaciones_json),
        comentario=resena.comentario,
        recomendaria=resena.recomendaria,
        queja_formal=resena.queja_formal,
        motivo_queja=resena.motivo_queja
        # created_at is populated automatically
    )
    db.add(nueva_resena)
    db.flush()
    
    if resena.queja_formal:
        profesor = db.query(Usuario).filter(Usuario.id == resena.profesor_id, Usuario.rol == 'profesor').first()
        if profesor:
            total_quejas = db.query(Resena).filter(Resena.profesor_id == profesor.id, Resena.queja_formal == True).count()
            penalidad = (total_quejas // 3) * 5
            profesor.score_confiabilidad = max(0, 100 - penalidad)
            
    db.commit()
    return {"message": "Reseña guardada exitosamente"}

@router.get("/estudiante/{estudiante_id}", response_model=List[ResenaEstudianteOut])
def get_resenas_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    resenas = db.query(Resena).filter(Resena.estudiante_id == estudiante_id).all()
    resultado = []
    
    for r in resenas:
        # Datos del profesor
        profesor = db.query(Usuario).filter(Usuario.id == r.profesor_id).first()
        prof_nombre = profesor.nombre if profesor else "Profesor Desconocido"
        
        # Datos de la sesión
        sesion = db.query(Sesion).filter(Sesion.id == r.sesion_id).first()
        curso_nombre = sesion.curso.nombre if sesion and sesion.curso else "Materia Desconocida"
        
        puntuaciones = {}
        try:
            if isinstance(r.puntuaciones_json, str):
                puntuaciones = json.loads(r.puntuaciones_json)
            elif isinstance(r.puntuaciones_json, dict):
                puntuaciones = r.puntuaciones_json
        except Exception:
            pass

        resultado.append(ResenaEstudianteOut(
            id=r.id,
            profesor_id=r.profesor_id,
            profesor_nombre=prof_nombre,
            sesion_id=r.sesion_id,
            curso_nombre=curso_nombre,
            puntuaciones_json=puntuaciones,
            comentario=r.comentario,
            recomendaria=bool(r.recomendaria),
            queja_formal=bool(r.queja_formal),
            motivo_queja=r.motivo_queja,
            fecha_creacion=r.created_at
        ))
        
    # Ordenar por fecha descendente
    resultado.sort(key=lambda x: x.fecha_creacion, reverse=True)
    return resultado

@router.get("/profesor/{profesor_id}")
def get_resenas_profesor(profesor_id: int, db: Session = Depends(get_db)):
    """Obtiene todas las reseñas de un profesor"""
    resenas = db.query(Resena).filter(Resena.profesor_id == profesor_id).all()
    resultado = []
    
    for r in resenas:
        estudiante = db.query(Usuario).filter(Usuario.id == r.estudiante_id).first()
        alumno_nombre = estudiante.nombre if estudiante else "Estudiante"
        
        puntuaciones = {}
        try:
            if isinstance(r.puntuaciones_json, str):
                puntuaciones = json.loads(r.puntuaciones_json)
            else:
                puntuaciones = r.puntuaciones_json
        except:
            puntuaciones = {}

        # Calcular estrellas promedio (promedio de subcategorías)
        estrellas = 0
        if puntuaciones:
            valores = list(puntuaciones.values())
            estrellas = round(sum(valores) / len(valores), 1) if valores else 0

        resultado.append({
            "id": r.id,
            "alumno": alumno_nombre,
            "comentario": r.comentario,
            "estrellas": estrellas,
            "fecha": r.created_at.strftime("%d/%m/%Y"),
            "queja_formal": r.queja_formal,
            "motivo_queja": r.motivo_queja,
            "respuesta_profesor": r.respuesta_profesor
        })
        
    resultado.sort(key=lambda x: x["fecha"], reverse=True)
    return resultado

class RespuestaProfesor(BaseModel):
    respuesta: str

@router.put("/{resena_id}/responder")
def responder_resena(resena_id: int, datos: RespuestaProfesor, db: Session = Depends(get_db)):
    resena = db.query(Resena).filter(Resena.id == resena_id).first()
    if not resena:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    
    resena.respuesta_profesor = datos.respuesta
    db.commit()
    return {"message": "Respuesta guardada exitosamente"}
