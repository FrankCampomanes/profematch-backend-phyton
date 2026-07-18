import sys
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:@localhost/profematch_db')
query_resenas = "SELECT profesor_id, puntuaciones_json, comentario, created_at FROM resenas ORDER BY created_at DESC"
df_resenas = pd.read_sql(query_resenas, engine)
print("Dtypes:")
print(df_resenas.dtypes)
print(f"Total resenas: {len(df_resenas)}")
resenas_prof_6 = df_resenas[df_resenas['profesor_id'] == 6]
print(f"Resenas for prof 6 count: {len(resenas_prof_6)}")
for _, r in resenas_prof_6.iterrows():
    print(r)
