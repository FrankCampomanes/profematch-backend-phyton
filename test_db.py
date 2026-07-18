import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:@localhost/profematch_db')
df_u = pd.read_sql("SELECT id, nombre, rol FROM usuarios WHERE nombre LIKE '%ejemplo%' OR nombre LIKE '%demo%'", engine)
print(df_u)
for pid in df_u['id']:
    print(f'Resenas for {pid}:')
    print(pd.read_sql(f"SELECT id, profesor_id, puntuaciones_json FROM resenas WHERE profesor_id={pid}", engine))
