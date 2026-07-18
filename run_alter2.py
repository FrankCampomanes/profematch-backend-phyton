from sqlalchemy import text
from core.database import engine

def run_migration():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE resenas ADD COLUMN respuesta_profesor TEXT NULL;"))
            print("Column respuesta_profesor added.")
        except Exception as e:
            print("respuesta_profesor might exist:", e)
        conn.commit()

if __name__ == "__main__":
    run_migration()
    print("Migration finished successfully.")
