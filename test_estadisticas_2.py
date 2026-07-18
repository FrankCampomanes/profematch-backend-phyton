import sys
import os

# Add backend dir to path
sys.path.append(r'd:\ProyectosUni\Lenguaje_Programacion\profematch-backend')

from routers.estadisticas import obtener_desempeno_profesores

try:
    print('Calling obtener_desempeno_profesores...')
    result = obtener_desempeno_profesores()
    for item in result:
        print(f"Profesor {item['nombre']}:")
        print(f" - Clases: {item['clases']}")
        print(f" - Calificacion: {item['calificacion']}")
        print(f" - Resenas count: {len(item.get('resenas', []))}")
        print(f" - Resenas: {item.get('resenas', [])}")
        print(f" - Radar: {item.get('metricasRadar', [])}")
except Exception as e:
    import traceback
    traceback.print_exc()
