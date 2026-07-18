from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List
from core.database import get_db
from models.all_models import Sesion, Inscripcion, Usuario
from schemas.core_schemas import SesionCreate, SesionOut, InscribirRequest, InscripcionOut, InscritoOut

router = APIRouter(prefix="/api/sesiones", tags=["Sesiones"])


def _build_sesion_out(s: Sesion, inscritos: int) -> SesionOut:
    return SesionOut(
        id=s.id,
        tema=s.tema,
        fecha_hora_inicio=s.fecha_hora_inicio,
        fecha_hora_fin=s.fecha_hora_fin,
        estado=s.estado,
        cupos_maximos=s.cupos_maximos,
        inscritos_actuales=inscritos,
        precio=s.precio,
        enlace_reunion=s.enlace_reunion,
        profesor_id=s.profesor_id,
        profesor_nombre=s.profesor.nombre if s.profesor else "Profesor",
        curso_nombre=s.curso.nombre if s.curso else "General"
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_sesion(sesion_data: SesionCreate, db: Session = Depends(get_db)):
    if not sesion_data.fecha_hora_inicio or not sesion_data.fecha_hora_fin:
        raise HTTPException(status_code=400, detail="Faltan datos requeridos (fechas)")

    inicio = sesion_data.fecha_hora_inicio
    fin = sesion_data.fecha_hora_fin

    # Quitar info de timezone para comparación (guardar como naive UTC)
    if inicio.tzinfo is not None:
        inicio = inicio.replace(tzinfo=None)
    if fin.tzinfo is not None:
        fin = fin.replace(tzinfo=None)

    diferencia_minutos = (fin - inicio).total_seconds() / 60
    if diferencia_minutos < 90:
        raise HTTPException(
            status_code=400,
            detail="Regla de negocio no cumplida: La sesión debe tener una duración mínima de 90 minutos (1.5 horas)."
        )

    # Validar cruce de horarios para el profesor
    # Una sesión se cruza si: (inicio < s.fin) y (fin > s.inicio)
    sesiones_existentes = db.query(Sesion).filter(
        Sesion.profesor_id == sesion_data.profesor_id,
        Sesion.estado.in_(['Programada', 'En Curso'])
    ).all()
    
    for s in sesiones_existentes:
        if inicio < s.fecha_hora_fin and fin > s.fecha_hora_inicio:
            raise HTTPException(
                status_code=400,
                detail=f"Cruce de horarios: Ya tienes una sesión programada de {s.fecha_hora_inicio.strftime('%H:%M')} a {s.fecha_hora_fin.strftime('%H:%M')}."
            )

    nueva_sesion = Sesion(
        profesor_id=sesion_data.profesor_id,
        curso_id=sesion_data.curso_id,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=fin,
        tema=sesion_data.tema,
        precio=sesion_data.precio,
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


@router.get("/disponibles", response_model=List[SesionOut])
def get_sesiones_disponibles(db: Session = Depends(get_db)):
    """Devuelve todas las sesiones con estado Programada (de todos los profesores)"""
    sesiones = db.query(Sesion).filter(Sesion.estado == 'Programada').all()
    result = []
    for s in sesiones:
        inscritos = db.query(Inscripcion).filter(
            Inscripcion.sesion_id == s.id,
            Inscripcion.estado == 'Confirmado'
        ).count()
        result.append(_build_sesion_out(s, inscritos))
    return result


@router.get("/estudiante/{estudiante_id}", response_model=List[InscripcionOut])
def get_inscripciones_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """Devuelve todas las inscripciones activas de un estudiante con datos de la sesión"""
    inscripciones = db.query(Inscripcion).filter(
        Inscripcion.estudiante_id == estudiante_id
    ).all()

    result = []
    for insc in inscripciones:
        s = insc.sesion
        if not s:
            continue
        result.append(InscripcionOut(
            inscripcion_id=insc.id,
            sesion_id=s.id,
            tema=s.tema,
            fecha_hora_inicio=s.fecha_hora_inicio,
            fecha_hora_fin=s.fecha_hora_fin,
            estado_sesion=s.estado,
            estado_inscripcion=insc.estado,
            precio=s.precio,
            enlace_reunion=s.enlace_reunion,
            profesor_id=s.profesor_id,
            profesor_nombre=s.profesor.nombre if s.profesor else "Profesor",
            curso_nombre=s.curso.nombre if s.curso else "General"
        ))
    return result


@router.put("/{id}/finalizar", status_code=status.HTTP_200_OK)
def finalizar_sesion(id: int, db: Session = Depends(get_db)):
    sesion = db.query(Sesion).filter(Sesion.id == id).first()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    if sesion.estado == 'Finalizada':
        raise HTTPException(status_code=400, detail="La sesión ya estaba finalizada")

    sesion.estado = 'Finalizada'
    db.commit()

    return {"message": "Sesión finalizada exitosamente"}


@router.post("/{id}/inscribir", status_code=status.HTTP_201_CREATED)
def inscribir_estudiante(id: int, request: InscribirRequest, db: Session = Depends(get_db)):
    sesion = db.query(Sesion).filter(Sesion.id == id).first()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    if sesion.estado != 'Programada':
        raise HTTPException(status_code=400, detail="No te puedes inscribir a una sesión que no está programada")

    # Verificar que el estudiante exista
    estudiante = db.query(Usuario).filter(
        Usuario.id == request.estudiante_id
    ).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Evitar inscripción duplicada
    ya_inscrito = db.query(Inscripcion).filter(
        Inscripcion.sesion_id == id,
        Inscripcion.estudiante_id == request.estudiante_id,
        Inscripcion.estado == 'Confirmado'
    ).first()
    if ya_inscrito:
        raise HTTPException(status_code=400, detail="Ya estás inscrito en esta sesión")

    # Validar cruce de horarios para el estudiante
    # Traer todas las inscripciones confirmadas del estudiante y revisar si alguna se cruza
    inscripciones_activas = db.query(Inscripcion).filter(
        Inscripcion.estudiante_id == request.estudiante_id,
        Inscripcion.estado == 'Confirmado'
    ).all()

    for insc in inscripciones_activas:
        if insc.sesion and insc.sesion.estado in ['Programada', 'En Curso']:
            # Verificar cruce (inicio1 < fin2) and (fin1 > inicio2)
            if sesion.fecha_hora_inicio < insc.sesion.fecha_hora_fin and sesion.fecha_hora_fin > insc.sesion.fecha_hora_inicio:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cruce de horarios: Ya estás inscrito en una sesión que interfiere (de {insc.sesion.fecha_hora_inicio.strftime('%H:%M')} a {insc.sesion.fecha_hora_fin.strftime('%H:%M')})."
                )

    # Verificar cupos
    inscritos_actuales = db.query(Inscripcion).filter(
        Inscripcion.sesion_id == id,
        Inscripcion.estado == 'Confirmado'
    ).count()
    if inscritos_actuales >= sesion.cupos_maximos:
        raise HTTPException(status_code=400, detail="La sesión ya no tiene cupos disponibles")

    nueva_inscripcion = Inscripcion(
        estudiante_id=request.estudiante_id,
        sesion_id=id,
        estado='Confirmado'
    )

    db.add(nueva_inscripcion)
    db.commit()

    return {"message": "Inscripción exitosa"}
@router.get("/{id}/inscritos", response_model=List[InscritoOut])
def get_sesion_inscritos(id: int, db: Session = Depends(get_db)):
    sesion = db.query(Sesion).filter(Sesion.id == id).first()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    inscripciones = db.query(Inscripcion).filter(
        Inscripcion.sesion_id == id,
        Inscripcion.estado != 'Cancelado'
    ).all()

    resultado = []
    for insc in inscripciones:
        usuario = db.query(Usuario).filter(Usuario.id == insc.estudiante_id).first()
        if usuario:
            resultado.append(InscritoOut(
                estudiante_id=usuario.id,
                nombre_estudiante=usuario.nombre,
                estado_inscripcion=insc.estado
            ))
            
    return resultado
