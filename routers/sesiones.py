from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from core.database import get_db
from models.all_models import Sesion
from schemas.core_schemas import SesionCreate

router = APIRouter(prefix="/api/sesiones", tags=["Sesiones"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_sesion(sesion_data: SesionCreate, db: Session = Depends(get_db)):
    if not sesion_data.fecha_hora_inicio or not sesion_data.fecha_hora_fin:
        raise HTTPException(status_code=400, detail="Faltan datos requeridos (fechas)")
        
    inicio = sesion_data.fecha_hora_inicio
    fin = sesion_data.fecha_hora_fin
    
    # Validar regla de los 90 minutos
    diferencia = fin - inicio
    diferencia_minutos = diferencia.total_seconds() / 60
    
    if diferencia_minutos < 90:
        raise HTTPException(
            status_code=400, 
            detail="Regla de negocio no cumplida: La sesión debe tener una duración mínima de 90 minutos (1.5 horas)."
        )
        
    nueva_sesion = Sesion(
        profesor_id=sesion_data.profesor_id,
        curso_id=sesion_data.curso_id,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=fin,
        cupos_maximos=sesion_data.cupos_maximos or 1,
        enlace_reunion=sesion_data.enlace_reunion,
        estado='Programada'
    )
    
    db.add(nueva_sesion)
    db.commit()
    db.refresh(nueva_sesion)
    
    return {
        "message": "Sesión creada exitosamente",
        "sesion_id": nueva_sesion.id
    }
