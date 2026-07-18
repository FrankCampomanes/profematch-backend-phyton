import pandas as pd
from sqlalchemy import create_engine
import json

engine = create_engine('mysql+pymysql://root:@localhost/profematch_db')
query_resenas = "SELECT profesor_id, puntuaciones_json, comentario, created_at FROM resenas ORDER BY created_at DESC"
df_resenas = pd.read_sql(query_resenas, engine)

resenas_prof = df_resenas[df_resenas['profesor_id'] == 6]
print("Reviews found:", len(resenas_prof))
for _, r in resenas_prof.iterrows():
    raw_puntajes = r['puntuaciones_json']
    print(f"RAW: {raw_puntajes}, TYPE: {type(raw_puntajes)}")
    puntajes = json.loads(raw_puntajes) if isinstance(raw_puntajes, str) else raw_puntajes
    print("PARSED:", puntajes)
