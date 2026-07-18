from sqlalchemy import text
from core.database import engine

def run_migration():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE resenas ADD COLUMN recomendaria BOOLEAN NOT NULL DEFAULT TRUE;"))
            print("Column recomendaria added.")
        except Exception as e:
            print("recomendaria might exist:", e)

        try:
            conn.execute(text("ALTER TABLE resenas ADD COLUMN queja_formal BOOLEAN NOT NULL DEFAULT FALSE;"))
            print("Column queja_formal added.")
        except Exception as e:
            print("queja_formal might exist:", e)

        try:
            conn.execute(text("ALTER TABLE resenas ADD COLUMN motivo_queja TEXT NULL;"))
            print("Column motivo_queja added.")
        except Exception as e:
            print("motivo_queja might exist:", e)
            
        conn.commit()

if __name__ == "__main__":
    run_migration()
    print("Migration finished successfully.")
