from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from models.all_models import Usuario, ProfesorPerfil, Curso, ProfesorCurso, Resena, Sesion, Inscripcion
from schemas.core_schemas import ProfesorListResponse, ProfesorUpdateProfile, ResenaItem, MetricasProfesor, SesionOut
from typing import List
from datetime import datetime, timedelta
import calendar

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
        
        sum_of_review_averages = 0.0
        
        for r in resenas_db:
            p_json = r.puntuaciones_json if r.puntuaciones_json else {}
            if isinstance(p_json, str):
                import json
                try: p_json = json.loads(p_json)
                except: p_json = {}
                
            rev_avg_estrellas = 0
            if p_json:
                vals = list(p_json.values())
                rev_avg = sum(vals) / len(vals)
                rev_avg_estrellas = round(rev_avg, 1)
                sum_of_review_averages += rev_avg
                
            lista_resenas.append(ResenaItem(
                id=r.id,
                estudiante=r.estudiante.nombre,
                comentario=r.comentario,
                fecha=r.created_at,
                puntuaciones=p_json,
                estrellas_calculadas=rev_avg_estrellas,
                respuesta_profesor=r.respuesta_profesor
            ))
            
            for k in criterios.keys():
                criterios[k] += p_json.get(k, 0)
                
        rating_global = 0.0
        tasa_aprobacion = "N/A"
        
        if len(resenas_db) > 0:
            for k in criterios.keys():
                criterios[k] = round(criterios[k] / len(resenas_db), 1)
            
            rating_global = round(sum_of_review_averages / len(resenas_db), 1)
            tasa_aprobacion = f"{int(round((rating_global / 5) * 100))}%"
            
        # Estadísticas reales por curso
        cursos_stats = []
        for c in prof.cursos:
            # Buscar la última sesión del curso para el precio
            ultima_sesion = db.query(Sesion).filter(
                Sesion.profesor_id == prof.id, 
                Sesion.curso_id == c.id
            ).order_by(Sesion.fecha_hora_inicio.desc()).first()
            precio_curso = ultima_sesion.precio if ultima_sesion else 0
            
            # Buscar reseñas específicas de este curso
            resenas_curso = db.query(Resena).filter(
                Resena.profesor_id == prof.id,
                Resena.sesion.has(curso_id=c.id)
            ).all()
            
            curso_avg = 0.0
            if resenas_curso:
                sum_avg = 0.0
                for rc in resenas_curso:
                    rc_json = rc.puntuaciones_json if rc.puntuaciones_json else {}
                    if isinstance(rc_json, str):
                        import json
                        try: rc_json = json.loads(rc_json)
                        except: rc_json = {}
                    if rc_json:
                        v = list(rc_json.values())
                        sum_avg += sum(v)/len(v)
                curso_avg = round(sum_avg / len(resenas_curso), 1)
                
            cursos_stats.append({
                "nombre": c.nombre,
                "precio": precio_curso,
                "rating": curso_avg
            })
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
            cursos=cursos_stats,
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

@router.get("/{id}/dashboard")
def get_profesor_dashboard(id: int, db: Session = Depends(get_db)):
    profesor = db.query(Usuario).filter(Usuario.id == id, Usuario.rol == 'profesor').first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    sesiones = db.query(Sesion).filter(Sesion.profesor_id == id).all()
    
    ingreso_neto = 0
    ingresos_pendientes = 0
    total_clases_dictadas = 0
    
    historial = []
    
    # Para gráficos
    ingresos_mes = {}
    ingresos_semana = {}
    
    now = datetime.now()
    
    for s in sesiones:
        inscripciones_confirmadas = db.query(Inscripcion).filter(
            Inscripcion.sesion_id == s.id, 
            Inscripcion.estado == 'Confirmado'
        ).count()
        
        pago_neto = inscripciones_confirmadas * s.precio
        
        if s.estado == 'Finalizada':
            ingreso_neto += pago_neto
            total_clases_dictadas += 1
            
            # Mes para gráfico
            mes_nombre = calendar.month_abbr[s.fecha_hora_inicio.month]
            if s.fecha_hora_inicio.year == now.year:
                ingresos_mes[mes_nombre] = ingresos_mes.get(mes_nombre, 0) + pago_neto
                
            # Semana del mes actual
            if s.fecha_hora_inicio.year == now.year and s.fecha_hora_inicio.month == now.month:
                # Aproximar a semana 1, 2, 3, 4
                semana = min((s.fecha_hora_inicio.day - 1) // 7 + 1, 4)
                label_semana = f"Semana {semana}"
                ingresos_semana[label_semana] = ingresos_semana.get(label_semana, 0) + pago_neto
                
        elif s.estado == 'Programada':
            ingresos_pendientes += pago_neto
            
        historial.append({
            "id": s.id,
            "fecha": s.fecha_hora_inicio.strftime("%Y-%m-%d %H:%M"),
            "tema": s.tema,
            "curso": s.curso.nombre if s.curso else "General",
            "inscritos": inscripciones_confirmadas,
            "precio": s.precio,
            "pagoNeto": pago_neto,
            "estado": s.estado
        })
        
    historial_ordenado = sorted(historial, key=lambda x: x["fecha"], reverse=True)
    
    # Construir datos fijos para el gráfico para que siempre hayan 4 semanas y 3 meses aunque esten en 0
    meses_labels = []
    for i in range(2, -1, -1):
        m = (now.month - i - 1) % 12 + 1
        meses_labels.append(calendar.month_abbr[m])
        
    line_data = [ingresos_mes.get(m, 0) for m in meses_labels]
    
    bar_labels = ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4']
    bar_data = [ingresos_semana.get(l, 0) for l in bar_labels]

    return {
        "finanzas": {
            "ingresoNeto": ingreso_neto,
            "ingresosPendientes": ingresos_pendientes,
            "bono": (total_clases_dictadas // 10) * 15,
        },
        "totalClasesDictadas": total_clases_dictadas,
        "historialTransacciones": historial_ordenado,
        "graficos": {
            "barLabels": bar_labels,
            "barData": bar_data,
            "lineLabels": meses_labels,
            "lineData": line_data
        }
    }

@router.get("/{id}/sesiones", response_model=List[SesionOut])
def get_profesor_sesiones(id: int, db: Session = Depends(get_db)):
    sesiones = db.query(Sesion).filter(Sesion.profesor_id == id).all()
    ahora = datetime.utcnow()
    resultado_actualizado = False

    for s in sesiones:
        # AUTO-FINALIZAR: Si la sesión está "Programada" y ya pasaron más de 60 min después del fin
        if s.estado == 'Programada' and s.fecha_hora_fin:
            limite_gracia = s.fecha_hora_fin + timedelta(minutes=60)
            if ahora > limite_gracia:
                s.estado = 'Finalizada'
                resultado_actualizado = True

    if resultado_actualizado:
        db.commit()

    sesiones_refrescadas = db.query(Sesion).filter(Sesion.profesor_id == id).all()
    result = []
    for s in sesiones_refrescadas:
        inscritos = db.query(Inscripcion).filter(Inscripcion.sesion_id == s.id, Inscripcion.estado == 'Confirmado').count()
        result.append(SesionOut(
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
        ))
    return result
