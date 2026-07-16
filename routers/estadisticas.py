from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
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
