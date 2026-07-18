from core.database import SessionLocal
from models.all_models import Usuario

def check():
    db = SessionLocal()
    users = db.query(Usuario).all()
    print("--- USERS IN DATABASE ---")
    for u in users:
        print(f"ID={u.id} | Name={u.nombre} | Email={u.email} | Rol={u.rol} | Estado={u.estado}")
    db.close()

if __name__ == "__main__":
    check()
