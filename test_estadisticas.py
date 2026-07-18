import sys
import os

# Add backend dir to path
sys.path.append(r'd:\ProyectosUni\Lenguaje_Programacion\profematch-backend')

from routers.estadisticas import obtener_desempeno_profesores

try:
    print('Calling obtener_desempeno_profesores...')
    result = obtener_desempeno_profesores()
    print('Success. Checking if JSON serializable...')
    import json
    from fastapi.encoders import jsonable_encoder
    json.dumps(jsonable_encoder(result))
    print('JSON serialization successful!')
except Exception as e:
    import traceback
    traceback.print_exc()
