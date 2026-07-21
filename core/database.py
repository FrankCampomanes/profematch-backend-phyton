import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "profematch_db")
DB_PORT = os.getenv("DB_PORT", "3306")

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Aiven da la URL como mysql://, pero SQLAlchemy necesita mysql+pymysql://
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # URL de conexión local
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para inyección de la base de datos en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
