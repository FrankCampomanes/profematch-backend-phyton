import sys
import os
from datetime import datetime, timedelta

# Asegurar que los imports funcionen si se ejecuta desde la raíz del backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models.all_models import Usuario, Sesion, Inscripcion, Curso

def fix_db():
    db = SessionLocal()
    try:
        # Encontrar al profesor demo
        profesor = db.query(Usuario).filter(Usuario.email == 'prof@profematch.com').first()
        if not profesor:
            print("Profesor no encontrado")
            return
            
        estudiante = db.query(Usuario).filter(Usuario.email == 'alumno@profematch.com').first()
        estudiante_id = estudiante.id if estudiante else 2
        
        curso = db.query(Curso).first()
        curso_id = curso.id if curso else 1

        print(f"Limpiando sesiones del profesor {profesor.id}...")
        
        # Eliminar todas las sesiones y sus inscripciones
        sesiones = db.query(Sesion).filter(Sesion.profesor_id == profesor.id).all()
        for s in sesiones:
            db.query(Inscripcion).filter(Inscripcion.sesion_id == s.id).delete()
            db.delete(s)
            
        db.commit()
        print("Sesiones borradas.")
        
        now = datetime.now()
        
        # Necesitamos 4 clases.
        # Semana 1: S/ 20
        # Semana 2: S/ 10
        # Semana 3: S/ 10
        # Programada: S/ 100
        
        # Para que caigan en Semana 1, el día debe ser entre 1 y 7
        fecha_sem1 = now.replace(day=3)
        # Para Semana 2, entre 8 y 14
        fecha_sem2 = now.replace(day=10)
        # Para Semana 3, entre 15 y 21
        fecha_sem3 = now.replace(day=18)
        # Programada, puede ser hoy o mañana
        fecha_prog = now + timedelta(days=1)
        
        sesiones_nuevas = [
            Sesion(
                profesor_id=profesor.id, curso_id=curso_id, 
                fecha_hora_inicio=fecha_sem1, fecha_hora_fin=fecha_sem1 + timedelta(hours=1.5),
                tema="Introducción (Semana 1)", precio=20, cupos_maximos=40,
                enlace_reunion="https://zoom.us/demo1", estado='Finalizada'
            ),
            Sesion(
                profesor_id=profesor.id, curso_id=curso_id, 
                fecha_hora_inicio=fecha_sem2, fecha_hora_fin=fecha_sem2 + timedelta(hours=1.5),
                tema="Conceptos Intermedios (Semana 2)", precio=10, cupos_maximos=40,
                enlace_reunion="https://zoom.us/demo2", estado='Finalizada'
            ),
            Sesion(
                profesor_id=profesor.id, curso_id=curso_id, 
                fecha_hora_inicio=fecha_sem3, fecha_hora_fin=fecha_sem3 + timedelta(hours=1.5),
                tema="Práctica Intensiva (Semana 3)", precio=10, cupos_maximos=40,
                enlace_reunion="https://zoom.us/demo3", estado='Finalizada'
            ),
            Sesion(
                profesor_id=profesor.id, curso_id=curso_id, 
                fecha_hora_inicio=fecha_prog, fecha_hora_fin=fecha_prog + timedelta(hours=1.5),
                tema="Masterclass Avanzada", precio=100, cupos_maximos=40,
                enlace_reunion="https://zoom.us/demo4", estado='Programada'
            )
        ]
        
        for s in sesiones_nuevas:
            db.add(s)
            
        db.commit()
        
        # Inscribir 1 alumno en cada clase para que se sume al pago_neto
        for s in sesiones_nuevas:
            inscripcion = Inscripcion(estudiante_id=estudiante_id, sesion_id=s.id, estado='Confirmado')
            db.add(inscripcion)
            
        db.commit()
        
        print("Base de datos limpia y poblada con 4 clases perfectas.")
        
    except Exception as e:
        print("Error:", str(e))
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_db()
