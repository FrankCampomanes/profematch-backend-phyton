from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from models.all_models import Usuario, Sesion, Inscripcion, Resena, Advertencia

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

@router.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    ahora = datetime.now()
    mes_actual = ahora.month
    anio_actual = ahora.year
    mes_nombre_es = f"{MESES_ES[mes_actual]} {anio_actual}"

    # --- 1. FINANZAS MENSUALES ---
    sesiones_mes = db.query(Sesion).filter(
        Sesion.estado == 'Finalizada',
        Sesion.fecha_hora_inicio != None
    ).all()

    sesiones_mes = [
        s for s in sesiones_mes
        if s.fecha_hora_inicio.month == mes_actual and s.fecha_hora_inicio.year == anio_actual
    ]

    caja_total = 0.0
    caja_docentes = 0.0
    comision_estudiantes = 0.0
    comision_docentes = 0.0

    for sesion in sesiones_mes:
        inscritos = db.query(Inscripcion).filter(
            Inscripcion.sesion_id == sesion.id,
            Inscripcion.estado == 'Confirmado'
        ).count()
        if inscritos > 0:
            precio_base = float(sesion.precio)
            total_base = precio_base * inscritos
            total_alumnos_pagan = total_base * 1.15

            com_est = total_base * 0.15
            com_doc = total_base * 0.10
            pago_neto_profe = total_base * 0.90

            caja_total += total_alumnos_pagan
            comision_estudiantes += com_est
            comision_docentes += com_doc
            caja_docentes += pago_neto_profe

    ganancia_neta = comision_estudiantes + comision_docentes

    # --- 2. INGRESOS SEMANALES ---
    ingresosSemanales = [0.0, 0.0, 0.0, 0.0]
    for sesion in sesiones_mes:
        inscritos = db.query(Inscripcion).filter(
            Inscripcion.sesion_id == sesion.id,
            Inscripcion.estado == 'Confirmado'
        ).count()
        if inscritos > 0 and sesion.fecha_hora_inicio:
            dias_diferencia = (ahora.date() - sesion.fecha_hora_inicio.date()).days
            precio_base = float(sesion.precio)
            ingreso_semana = (precio_base * inscritos * 0.15) + (precio_base * inscritos * 0.10)

            if 0 <= dias_diferencia < 7:
                ingresosSemanales[3] += ingreso_semana
            elif 7 <= dias_diferencia < 14:
                ingresosSemanales[2] += ingreso_semana
            elif 14 <= dias_diferencia < 21:
                ingresosSemanales[1] += ingreso_semana
            elif 21 <= dias_diferencia < 28:
                ingresosSemanales[0] += ingreso_semana

    # --- 3. ACTIVIDAD DE LA COMUNIDAD ---
    profesores_total = db.query(Usuario).filter(Usuario.rol == 'profesor').count()
    estudiantes_total = db.query(Usuario).filter(Usuario.rol == 'estudiante').count()
    profesores_activos = db.query(Sesion.profesor_id).distinct().count()
    estudiantes_activos = db.query(Inscripcion.estudiante_id).distinct().count()

    salud_comunidad = {
        "profesores_activos": profesores_activos,
        "profesores_inactivos": max(0, profesores_total - profesores_activos),
        "estudiantes_activos": estudiantes_activos,
        "estudiantes_inactivos": max(0, estudiantes_total - estudiantes_activos)
    }

    # --- 4. QUEJAS FORMALES ---
    quejas_db = db.query(Resena).filter(Resena.queja_formal == True).order_by(Resena.created_at.desc()).all()
    historial_auditoria = []

    for q in quejas_db:
        acusado_nombre = q.profesor.nombre if q.profesor else "Profesor Desconocido"
        # Revisar si tiene una advertencia vinculada
        warning = db.query(Advertencia).filter(Advertencia.resena_id == q.id).first()
        
        estado = "En Revisión"
        if warning:
            estado = "Advertencia Leída" if warning.leida else "Advertido"
        elif q.respuesta_profesor:
            estado = "Respondida"

        historial_auditoria.append({
            "id": f"Q-{q.id}",
            "resena_id": q.id,
            "fecha": q.created_at.strftime("%Y-%m-%d") if q.created_at else "Desconocida",
            "acusado": acusado_nombre,
            "profesor_id": q.profesor_id,
            "motivo": q.motivo_queja if q.motivo_queja else "Motivo no especificado",
            "estado": estado
        })

    moderacion = {
        "quejasPendientes": len([q for q in historial_auditoria if q["estado"] == "En Revisión"])
    }

    return {
        "finanzas": {
            "cajaTotal": round(caja_total, 2),
            "comisionEstudiantes": round(comision_estudiantes, 2),
            "comisionDocentes": round(comision_docentes, 2),
            "gananciaNeta": round(ganancia_neta, 2),
            "caja_docentes": round(caja_docentes, 2),
        },
        "periodo": {
            "mes": mes_nombre_es,
            "mes_num": mes_actual,
            "anio": anio_actual
        },
        "moderacion": moderacion,
        "ingresosSemanales": [round(v, 2) for v in ingresosSemanales],
        "saludComunidad": salud_comunidad,
        "historialAuditoria": historial_auditoria
    }


@router.post("/advertencias")
def enviar_advertencia(payload: dict, db: Session = Depends(get_db)):
    """El admin envía una advertencia a un profesor"""
    profesor_id = payload.get("profesor_id")
    mensaje = payload.get("mensaje", "").strip()
    admin_id = payload.get("admin_id")
    resena_id = payload.get("resena_id")

    if not profesor_id or not mensaje:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Faltan datos: profesor_id y mensaje son requeridos.")

    advertencia = Advertencia(
        profesor_id=profesor_id,
        admin_id=admin_id,
        resena_id=resena_id,
        mensaje=mensaje,
        leida=False
    )
    db.add(advertencia)
    db.commit()
    db.refresh(advertencia)

    return {"ok": True, "advertencia_id": advertencia.id, "mensaje": "Advertencia enviada correctamente."}


@router.get("/advertencias/profesor/{profesor_id}")
def get_advertencias_profesor(profesor_id: int, db: Session = Depends(get_db)):
    """El profesor consulta sus advertencias pendientes"""
    advertencias = db.query(Advertencia).filter(
        Advertencia.profesor_id == profesor_id
    ).order_by(Advertencia.created_at.desc()).all()

    return [
        {
            "id": a.id,
            "mensaje": a.mensaje,
            "leida": a.leida,
            "fecha": a.created_at.strftime("%d/%m/%Y %H:%M") if a.created_at else ""
        }
        for a in advertencias
    ]


@router.put("/advertencias/{advertencia_id}/marcar-leida")
def marcar_advertencia_leida(advertencia_id: int, db: Session = Depends(get_db)):
    """Marca una advertencia como leída"""
    adv = db.query(Advertencia).filter(Advertencia.id == advertencia_id).first()
    if adv:
        adv.leida = True
        db.commit()
    return {"ok": True}
