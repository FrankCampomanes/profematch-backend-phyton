from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import json
from core.database import get_db, engine

router = APIRouter(prefix="/api/admin/estadisticas", tags=["Estadísticas (Admin/Pandas)"])

@router.get("/")
def obtener_estadisticas():
    # Extraemos datos para el Dashboard de Admin
    query_usuarios = "SELECT rol, estado, score_confiabilidad FROM usuarios"
    query_sesiones = "SELECT estado, cupos_maximos FROM sesiones"
    
    df_usuarios = pd.read_sql(query_usuarios, engine)
    df_sesiones = pd.read_sql(query_sesiones, engine)
    
    # 1. Estadísticas de Usuarios
    total_usuarios = len(df_usuarios)
    roles_distribucion = df_usuarios['rol'].value_counts().to_dict() if not df_usuarios.empty else {}
    promedio_confiabilidad = df_usuarios['score_confiabilidad'].mean() if not df_usuarios.empty else 0
    
    # 2. Estadísticas de Sesiones
    total_sesiones = len(df_sesiones)
    estados_sesion = df_sesiones['estado'].value_counts().to_dict() if not df_sesiones.empty else {}
    
    return {
        "usuarios": {
            "total": total_usuarios,
            "distribucion_por_rol": roles_distribucion,
            "promedio_confiabilidad_global": round(promedio_confiabilidad, 2)
        },
        "sesiones": {
            "total": total_sesiones,
            "distribucion_por_estado": estados_sesion
        }
    }

from datetime import datetime
import json

@router.get("/global_kpis")
def obtener_kpis_globales():
    mes_actual = datetime.now().month
    year_actual = datetime.now().year
    
    query_sesiones = "SELECT id, estado, fecha_hora_inicio FROM sesiones"
    df_sesiones = pd.read_sql(query_sesiones, engine)
    
    query_inscripciones = "SELECT sesion_id FROM inscripciones"
    df_inscripciones = pd.read_sql(query_inscripciones, engine)
    
    if not df_sesiones.empty:
        df_sesiones['fecha_hora_inicio'] = pd.to_datetime(df_sesiones['fecha_hora_inicio'])
        df_mes_actual = df_sesiones[
            (df_sesiones['fecha_hora_inicio'].dt.month == mes_actual) & 
            (df_sesiones['fecha_hora_inicio'].dt.year == year_actual) &
            (df_sesiones['estado'] == 'Finalizada')
        ]
        clases_impartidas = len(df_mes_actual)
        
        if not df_inscripciones.empty and not df_mes_actual.empty:
            # Filtrar inscripciones cuyas sesiones estan en df_mes_actual
            sesiones_finalizadas_ids = df_mes_actual['id'].tolist()
            alumnos_atendidos = len(df_inscripciones[df_inscripciones['sesion_id'].isin(sesiones_finalizadas_ids)])
        else:
            alumnos_atendidos = 0
    else:
        clases_impartidas = 0
        alumnos_atendidos = 0
        
    query_resenas = "SELECT puntuaciones_json FROM resenas"
    df_resenas = pd.read_sql(query_resenas, engine)
    
    calidad_promedio = 0.0
    if not df_resenas.empty:
        promedios = []
        for index, row in df_resenas.iterrows():
            try:
                puntajes = json.loads(row['puntuaciones_json']) if isinstance(row['puntuaciones_json'], str) else row['puntuaciones_json']
                if isinstance(puntajes, dict):
                    vals = [v for v in puntajes.values() if isinstance(v, (int, float))]
                    if vals:
                        promedios.append(sum(vals)/len(vals))
            except Exception:
                pass
        if promedios:
            calidad_promedio = sum(promedios) / len(promedios)
            
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    # Calculo para el gráfico de volumen de clases
    volumen_semanas = [0, 0, 0, 0]
    if not df_sesiones.empty:
        # Semanas (1, 2, 3, 4) del mes actual
        for _, s in df_sesiones.iterrows():
            if pd.notnull(s['fecha_hora_inicio']) and s['fecha_hora_inicio'].month == mes_actual and s['fecha_hora_inicio'].year == year_actual and s['estado'] == 'Finalizada':
                dia = s['fecha_hora_inicio'].day
                semana = min((dia - 1) // 7, 3) # Agrupa en 0, 1, 2, 3 (max 4 semanas)
                volumen_semanas[semana] += 1
                
    return {
        "clases_impartidas": clases_impartidas,
        "alumnos_atendidos": alumnos_atendidos,
        "calidad_promedio": round(calidad_promedio, 1),
        "mes_actual": meses[mes_actual - 1],
        "volumen_semanas": volumen_semanas
    }

@router.get("/desempeno_profesores")
def obtener_desempeno_profesores():
    # Obtener usuarios (profesores)
    query_profesores = """
        SELECT u.id, u.nombre, p.descripcion, p.universidad
        FROM usuarios u
        JOIN profesores_perfiles p ON u.id = p.usuario_id
        WHERE u.rol = 'profesor'
    """
    df_profesores = pd.read_sql(query_profesores, engine)
    
    if df_profesores.empty:
        return []

    # Cursos de los profesores (para sacar la facultad/categoría)
    query_prof_cursos = "SELECT profesor_id, curso_id FROM profesores_cursos"
    df_prof_cursos = pd.read_sql(query_prof_cursos, engine)
    
    query_cursos = "SELECT id as curso_id, categoria as facultad FROM cursos"
    df_cursos = pd.read_sql(query_cursos, engine)
    
    # Unir para obtener la facultad
    facultades = {}
    if not df_prof_cursos.empty and not df_cursos.empty:
        df_facultades = pd.merge(df_prof_cursos, df_cursos, on='curso_id')
        for prof_id, group in df_facultades.groupby('profesor_id'):
            facs = group['facultad'].unique()
            facultades[prof_id] = ", ".join(facs)

    # Sesiones finalizadas
    query_sesiones = "SELECT id as sesion_id, profesor_id, estado FROM sesiones WHERE estado = 'Finalizada'"
    df_sesiones = pd.read_sql(query_sesiones, engine)
    
    # Inscripciones
    query_inscripciones = "SELECT sesion_id FROM inscripciones"
    df_inscripciones = pd.read_sql(query_inscripciones, engine)

    # Reseñas
    query_resenas = "SELECT profesor_id, puntuaciones_json, comentario, created_at FROM resenas ORDER BY created_at DESC"
    df_resenas = pd.read_sql(query_resenas, engine)

    resultados = []
    
    for index, row in df_profesores.iterrows():
        prof_id = int(row['id'])
        nombre = row['nombre']
        facultad = facultades.get(prof_id, "General")
        
        # Clases dictadas
        clases_dictadas = 0
        sesiones_del_prof = []
        if not df_sesiones.empty:
            sesiones_prof_df = df_sesiones[df_sesiones['profesor_id'] == prof_id]
            clases_dictadas = len(sesiones_prof_df)
            sesiones_del_prof = sesiones_prof_df['sesion_id'].tolist()
            
        # Alumnos impactados
        alumnos_impactados = 0
        if not df_inscripciones.empty and sesiones_del_prof:
            alumnos_impactados = len(df_inscripciones[df_inscripciones['sesion_id'].isin(sesiones_del_prof)])
            
        # Calificación y Análisis
        calificacion_promedio = 0.0
        analisis = "Estable"
        resenas_prof_list = []
        criterios = {"Puntualidad": 0, "Claridad": 0, "Dominio": 0, "Profesionalismo": 0, "Exigencia": 0, "Disponibilidad": 0}
        
        if not df_resenas.empty:
            resenas_prof = df_resenas[df_resenas['profesor_id'] == int(prof_id)]
            if not resenas_prof.empty:
                promedios = []
                for _, r in resenas_prof.iterrows():
                    try:
                        raw_puntajes = r['puntuaciones_json']
                        if pd.isna(raw_puntajes) or not raw_puntajes:
                            continue
                            
                        puntajes = raw_puntajes
                        while isinstance(puntajes, str):
                            try:
                                puntajes = json.loads(puntajes)
                            except:
                                break
                                
                        if isinstance(puntajes, dict):
                            vals = []
                            for k, v in puntajes.items():
                                try:
                                    num_v = float(v)
                                    vals.append(num_v)
                                    if k in criterios:
                                        criterios[k] += num_v
                                except (ValueError, TypeError):
                                    pass
                            if vals:
                                rev_avg = sum(vals)/len(vals)
                                promedios.append(rev_avg)
                                
                                resenas_prof_list.append({
                                    "autor": "Estudiante", 
                                    "curso": "General", 
                                    "fecha": str(r.get('created_at', '')).split()[0],
                                    "criterios": puntajes,
                                    "comentario": str(r.get('comentario', '')),
                                    "estrellas_calculadas": round(rev_avg, 1)
                                })
                    except:
                        pass
                        
                if promedios:
                    calificacion_promedio = sum(promedios) / len(promedios)
                    # Análisis simple: comparando las ultimas 5 reseñas vs el promedio
                    ultimas_5 = promedios[:5]
                    promedio_reciente = sum(ultimas_5) / len(ultimas_5)
                    if promedio_reciente > calificacion_promedio:
                        analisis = "sube"
                    elif promedio_reciente < calificacion_promedio:
                        analisis = "baja"
                    else:
                        analisis = "mantiene"
                        
                    for k in criterios.keys():
                        criterios[k] = round(criterios[k] / len(promedios), 1)
                        
        metricas_radar = [
            criterios.get("Puntualidad", 0),
            criterios.get("Claridad", 0),
            criterios.get("Dominio", 0),
            criterios.get("Profesionalismo", 0),
            criterios.get("Exigencia", 0),
            criterios.get("Disponibilidad", 0)
        ]
                        
        univ = row.get('universidad')
        desc = row.get('descripcion')
        
        univ_str = str(univ) if pd.notnull(univ) and univ != "" else "No especificado"
        desc_str = str(desc) if pd.notnull(desc) and desc != "" else "Sin información académica registrada."
        
        resultados.append({
            "id": prof_id,
            "nombre": nombre,
            "facultad": facultad,
            "clasesDadas": clases_dictadas,
            "alumnosAtendidos": alumnos_impactados,
            "calificacion": round(calificacion_promedio, 1),
            "tendencia": analisis,
            "universidades": [univ_str],
            "infoAcademica": desc_str,
            "resenas": resenas_prof_list,
            "tutorias": [],
            "metricasRadar": metricas_radar
        })
        
    return resultados
