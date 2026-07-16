from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from models.all_models import Usuario, ProfesorPerfil, Curso, ProfesorCurso, Resena, Sesion, Inscripcion
from schemas.core_schemas import ProfesorListResponse, ProfesorUpdateProfile, ResenaItem, MetricasProfesor
from typing import List

router = APIRouter(prefix="/api/professors", tags=["Profesores"])

@router.get("/", response_model=List[ProfesorListResponse])
def get_profesores(db: Session = Depends(get_db)):
    # Buscar todos los profesores aprobados y con perfil completado
    profesores_db = db.query(Usuario).filter(
        Usuario.rol == 'profesor',
        Usuario.estado == 'aprobado'
    ).join(ProfesorPerfil).filter(
        ProfesorPerfil.perfil_completado == True
    ).all()
    
    resultados = []
    
    for prof in profesores_db:
        perfil = prof.perfil
        cursos_nombres = [c.nombre for c in prof.cursos]
        
        # Calcular estudiantes atendidos
        # Sesiones finalizadas del profesor -> inscripciones confirmadas
        estudiantes_atendidos = db.query(func.count(func.distinct(Inscripcion.estudiante_id)))\
            .join(Sesion, Sesion.id == Inscripcion.sesion_id)\
            .filter(Sesion.profesor_id == prof.id, Sesion.estado == 'Finalizada', Inscripcion.estado == 'Confirmado')\
            .scalar() or 0
            
        # Obtener reseñas
        resenas_db = db.query(Resena).filter(Resena.profesor_id == prof.id).all()
        lista_resenas = []
        criterios = {"Claridad": 0, "Dominio": 0, "Puntualidad": 0, "Profesionalismo": 0, "Exigencia": 0, "Disponibilidad": 0}
        
        for r in resenas_db:
            p_json = r.puntuaciones_json if r.puntuaciones_json else {}
            if isinstance(p_json, str):
                import json
                try: p_json = json.loads(p_json)
                except: p_json = {}
                
            lista_resenas.append(ResenaItem(
                estudiante=r.estudiante.nombre,
                comentario=r.comentario,
                fecha=r.created_at,
                puntuaciones=p_json
            ))
            
            for k in criterios.keys():
                criterios[k] += p_json.get(k, 0)
                
        rating_global = 0.0
        tasa_aprobacion = "N/A"
        
        if len(resenas_db) > 0:
            for k in criterios.keys():
                criterios[k] = round(criterios[k] / len(resenas_db), 1)
            
            total_suma = sum(criterios.values())
            rating_global = round(total_suma / 6, 1)
            tasa_aprobacion = f"{int(round((rating_global / 5) * 100))}%"
            
        metricas = MetricasProfesor(
            estudiantesAtendidos=estudiantes_atendidos,
            tasaAprobacion=tasa_aprobacion,
            tiempoRespuesta="N/A"
        )
        
        reconocimientos = perfil.reconocimientos if perfil.reconocimientos else []
        if isinstance(reconocimientos, str):
            import json
            try: reconocimientos = json.loads(reconocimientos)
            except: reconocimientos = []
            
        horarios = perfil.horarios if perfil.horarios else {}
        if isinstance(horarios, str):
            import json
            try: horarios = json.loads(horarios)
            except: horarios = {}

        resultados.append(ProfesorListResponse(
            id=prof.id,
            nombre=prof.nombre,
            email=prof.email,
            descripcion=perfil.descripcion,
            metodologia=perfil.metodologia,
            universidad=perfil.universidad,
            foto=perfil.foto,
            perfil_completado=perfil.perfil_completado,
            reconocimientos=reconocimientos,
            horarios=horarios,
            cursos=cursos_nombres,
            rating=rating_global,
            criteriosEvaluacion=criterios,
            resenas=lista_resenas,
            metricas=metricas
        ))
        
    return resultados

@router.put("/{id}/profile")
def update_profile(id: int, profile_data: ProfesorUpdateProfile, db: Session = Depends(get_db)):
    perfil = db.query(ProfesorPerfil).filter(ProfesorPerfil.usuario_id == id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
        
    perfil.descripcion = profile_data.descripcion
    perfil.metodologia = profile_data.metodologia
    perfil.reconocimientos = profile_data.reconocimientos
    perfil.horarios = profile_data.horarios
    perfil.perfil_completado = True
    
    # Actualizar cursos
    db.query(ProfesorCurso).filter(ProfesorCurso.profesor_id == id).delete()
    
    if profile_data.cursos:
        for nombre_curso in profile_data.cursos:
            curso = db.query(Curso).filter(Curso.nombre == nombre_curso).first()
            if curso:
                db.add(ProfesorCurso(profesor_id=id, curso_id=curso.id))
                
    db.commit()
    return {"message": "Perfil actualizado exitosamente"}
