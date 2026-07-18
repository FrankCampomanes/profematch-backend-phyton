import sys
import os
from datetime import datetime, timedelta
import random

# Add current path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models.all_models import Usuario, Sesion, Inscripcion, Curso

def seed_demo():
    db = SessionLocal()
    
    # Verify prof exists
    profesor = db.query(Usuario).filter(Usuario.email == 'prof@profematch.com', Usuario.rol == 'profesor').first()
    estudiante = db.query(Usuario).filter(Usuario.email == 'estu@profematch.com', Usuario.rol == 'estudiante').first()
    
    if not profesor or not estudiante:
        print("Demo accounts not found by email (prof@profematch.com, estu@profematch.com). Cannot seed data.")
        db.close()
        return

    # Check if prof already has sessions
    sesiones_existentes = db.query(Sesion).filter(Sesion.profesor_id == profesor.id).count()
    if sesiones_existentes > 0:
        print(f"Profesor already has {sesiones_existentes} sessions. No need to seed.")
        db.close()
        return
        
    print("Seeding realistic demo data for Profesor Demo...")
    
    # Need a course
    curso = db.query(Curso).first()
    curso_id = curso.id if curso else 1
    
    now = datetime.now()
    
    # Create 3 past sessions (Finalizadas)
    temas_pasados = ["Introducción a Python", "Estructuras de Datos", "POO Avanzada"]
    for i, tema in enumerate(temas_pasados):
        # 1 week ago, 2 weeks ago, 3 weeks ago
        fecha_inicio = now - timedelta(days=(i+1)*7)
        fecha_fin = fecha_inicio + timedelta(hours=2)
        precio = random.choice([10, 12, 15])
        
        s = Sesion(
            profesor_id=profesor.id,
            curso_id=curso_id,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            tema=tema,
            precio=precio,
            cupos_maximos=10,
            enlace_reunion="https://meet.google.com/demo",
            estado='Finalizada'
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        
        # Inscribe student
        ins = Inscripcion(
            estudiante_id=estudiante.id,
            sesion_id=s.id,
            estado='Confirmado'
        )
        db.add(ins)
        db.commit()

    # Create 1 future session (Programada)
    fecha_inicio_futura = now + timedelta(days=2)
    s_futura = Sesion(
        profesor_id=profesor.id,
        curso_id=curso_id,
        fecha_hora_inicio=fecha_inicio_futura,
        fecha_hora_fin=fecha_inicio_futura + timedelta(hours=2),
        tema="Desarrollo Web con FastAPI",
        precio=15,
        cupos_maximos=10,
        enlace_reunion="https://meet.google.com/demo-future",
        estado='Programada'
    )
    db.add(s_futura)
    db.commit()
    db.refresh(s_futura)
    
    ins_futura = Inscripcion(
        estudiante_id=estudiante.id,
        sesion_id=s_futura.id,
        estado='Confirmado'
    )
    db.add(ins_futura)
    db.commit()
    
    print("Successfully seeded 3 Finalizadas sessions and 1 Programada session.")
    db.close()

if __name__ == "__main__":
    seed_demo()
