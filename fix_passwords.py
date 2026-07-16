"""
Script temporal para regenerar los hashes de contraseñas en la base de datos.
Las contraseñas anteriores fueron creadas con passlib que es incompatible
con bcrypt >= 4.1. Este script las regenera usando bcrypt directamente.
"""
import bcrypt
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "profematch_db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

# Contraseñas demo que deben funcionar
demo_users = {
    "admin@profematch.com": "admin123",
    "prof@profematch.com": "prof123",
    "estu@profematch.com": "estu123",
}

conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT,
)

cursor = conn.cursor()

for email, password in demo_users.items():
    new_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cursor.execute(
        "UPDATE usuarios SET password_hash = %s WHERE email = %s",
        (new_hash, email),
    )
    rows = cursor.rowcount
    if rows > 0:
        print(f"OK - {email} actualizado")
    else:
        print(f"SKIP - {email} no existe en la base de datos")

conn.commit()
cursor.close()
conn.close()
print("Listo. Contraseñas regeneradas.")
