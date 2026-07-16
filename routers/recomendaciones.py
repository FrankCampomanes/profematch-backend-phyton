from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import pandas as pd
from core.database import get_db, engine
from pydantic import BaseModel

router = APIRouter(prefix="/api/recomendaciones", tags=["Algoritmo Inteligente (Pandas)"])

class RecomendacionResponse(BaseModel):
    profesor_id: int
    nombre: str
    score_confiabilidad: float
    promedio_rating: float
    match_score: float

@router.get("/", response_model=List[RecomendacionResponse])
def recomendar_profesores(curso_id: Optional[int] = None, db: Session = Depends(get_db)):
    # 1. Extraer datos con SQL puro hacia un DataFrame de Pandas
    query_profesores = """
        SELECT u.id as profesor_id, u.nombre, u.score_confiabilidad 
        FROM usuarios u
        JOIN profesores_perfiles p ON u.id = p.usuario_id
        WHERE u.rol = 'profesor' AND u.estado = 'aprobado' AND p.perfil_completado = 1
    """
    
    if curso_id:
        query_profesores = f"""
            SELECT u.id as profesor_id, u.nombre, u.score_confiabilidad 
            FROM usuarios u
            JOIN profesores_perfiles p ON u.id = p.usuario_id
            JOIN profesores_cursos pc ON u.id = pc.profesor_id
            WHERE u.rol = 'profesor' AND u.estado = 'aprobado' AND p.perfil_completado = 1 
            AND pc.curso_id = {curso_id}
        """
        
    df_prof = pd.read_sql(query_profesores, engine)
    
    if df_prof.empty:
        return []

    query_resenas = "SELECT profesor_id, puntuaciones_json FROM resenas"
    df_resenas = pd.read_sql(query_resenas, engine)
    
    # 2. Procesamiento de Datos con Pandas (Ciencia de Datos)
    # Convertir JSON a puntaje promedio
    def extract_avg_rating(json_str):
        if not json_str: return 0.0
        import json
        try:
            data = json.loads(json_str)
            if not data: return 0.0
            return sum(data.values()) / len(data)
        except:
            return 0.0

    if not df_resenas.empty:
        df_resenas['avg_rating'] = df_resenas['puntuaciones_json'].apply(extract_avg_rating)
        # Agrupar por profesor y sacar promedio de todas sus reseñas
        df_resenas_grouped = df_resenas.groupby('profesor_id')['avg_rating'].mean().reset_index()
    else:
        df_resenas_grouped = pd.DataFrame(columns=['profesor_id', 'avg_rating'])

    # Unir DataFrames (Merge)
    df_merged = pd.merge(df_prof, df_resenas_grouped, on='profesor_id', how='left')
    
    # Rellenar NaNs con 0
    df_merged['avg_rating'] = df_merged['avg_rating'].fillna(0.0)
    
    # 3. Aplicar Algoritmo Matemático de Ponderación (Programación Funcional con Lambdas)
    # - 60% peso a las reseñas
    # - 40% peso al score de confiabilidad (normalizado a escala de 5, asumiendo max 100)
    df_merged['match_score'] = df_merged.apply(
        lambda row: round((row['avg_rating'] * 0.6) + ((row['score_confiabilidad'] / 100 * 5) * 0.4), 2),
        axis=1
    )
    
    # Ordenar por el Match Score de mayor a menor
    df_sorted = df_merged.sort_values(by='match_score', ascending=False)
    
    # Convertir el DataFrame resultante a una lista de diccionarios para responder
    resultados = df_sorted.to_dict('records')
    return resultados
