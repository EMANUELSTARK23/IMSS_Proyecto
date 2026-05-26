# scripts/03_pipelines.py 
# Aggregation Pipelines del IMSS ejecutados desde Python con pymongo 

from pymongo import MongoClient 
from dotenv import load_dotenv 
import os 

load_dotenv() 

def conectar_local(): 
    client = MongoClient(os.getenv('MONGO_LOCAL_URI')) 
    return client[os.getenv('MONGO_LOCAL_DB')][os.getenv('COLECCION')] 

def conectar_atlas(): 
    client = MongoClient(os.getenv('MONGO_ATLAS_URI')) 
    return client[os.getenv('MONGO_ATLAS_DB')][os.getenv('COLECCION')] 

# Pipeline 1 — Top entidades por asegurados (año más reciente) 
def p1_por_entidad(col, anio=2024) -> list: 
    return list(col.aggregate([ 
        { '$match': { 'anio': anio } }, 
        { '$group': { '_id': '$entidad', 'total': { '$sum': '$total_asegurados' } } }, 
        { '$sort': { 'total': -1 } } 
    ])) 

# Pipeline 2 — Evolución mensual nacional 
def p2_evolucion_temporal(col) -> list: 
    return list(col.aggregate([ 
        { '$group': { 
            '_id': { 'anio': '$anio', 'mes': '$mes' }, 
            'total': { '$sum': '$total_asegurados' } 
        }}, 
        { '$sort': { '_id.anio': 1, '_id.mes': 1 } }, 
        { '$project': { '_id': 0, 'anio': '$_id.anio', 'mes': '$_id.mes', 'total': 1 } } 
    ])) 

# Pipeline 3 — Por sexo 
def p3_por_sexo(col) -> list: 
    return list(col.aggregate([ 
        { '$group': { 
            '_id': '$sexo', 
            'total': { '$sum': '$total_asegurados' }, 
            'promedio': { '$avg': '$total_asegurados' } 
        }}, 
        { '$sort': { 'total': -1 } } 
    ])) 

# Pipeline 4 — Tipo de trabajador 2024 
def p4_tipo_trabajador(col, anio=2024) -> list: 
    return list(col.aggregate([ 
        { '$match': { 'anio': anio } }, 
        { '$group': { 
            '_id': None, 
            'perm_urbanos': { '$sum': '$permanentes_urbanos' }, 
            'perm_campo':   { '$sum': '$permanentes_campo' }, 
            'even_urbanos': { '$sum': '$eventuales_urbanos' }, 
            'even_campo':   { '$sum': '$eventuales_campo' }, 
            'total':        { '$sum': '$total_asegurados' } 
        }} 
    ])) 

# Pipeline 5 — Por región con masa salarial 
def p5_por_region(col, anio=2024) -> list: 
    return list(col.aggregate([ 
        { '$match': { 'anio': anio } }, 
        { '$group': { 
            '_id': '$region', 
            'total': { '$sum': '$total_asegurados' }, 
            'masa_salarial': { '$sum': '$masa_salarial_total' } 
        }}, 
        { '$sort': { 'total': -1 } } 
    ])) 

# Pipeline 6 — Top crecimiento 2015 vs 2024 
def p6_top_crecimiento(col) -> list: 
    return list(col.aggregate([ 
        { '$match': { 'anio': { '$in': [2015, 2024] } } }, 
        { '$group': { 
            '_id': { 'entidad': '$entidad', 'anio': '$anio' }, 
            'total': { '$sum': '$total_asegurados' } 
        }}, 
        { '$group': { 
            '_id': '$_id.entidad', 
            'datos': { '$push': { 'anio': '$_id.anio', 'total': '$total' } } 
        }}, 
        { '$project': { 
            'crecimiento_abs': { 
                '$subtract': [ 
                    { '$arrayElemAt': ['$datos.total', 1] }, 
                    { '$arrayElemAt': ['$datos.total', 0] } 
                ] 
            } 
        }}, 
        { '$sort': { 'crecimiento_abs': -1 } }, 
        { '$limit': 10 } 
    ])) 

if __name__ == '__main__': 
    # Asegúrate de tener tu archivo .env configurado correctamente
    col = conectar_local() 
    
    pipelines = { 
        'P1 — Por entidad (2024)':    p1_por_entidad(col), 
        'P2 — Evolución temporal':    p2_evolucion_temporal(col), 
        'P3 — Por sexo':              p3_por_sexo(col), 
        'P4 — Tipo trabajador (2024)':p4_tipo_trabajador(col), 
        'P5 — Por región (2024)':     p5_por_region(col), 
        'P6 — Top crecimiento':       p6_top_crecimiento(col), 
    } 
    
    for nombre, datos in pipelines.items(): 
        print(f'\n── {nombre} ({len(datos)} resultados) ──') 
        # Imprime solo los primeros 3 resultados de cada pipeline para no saturar la consola
        for fila in datos[:3]: 
            print(f'   {fila}') 
            
    print('\nPipelines ejecutados correctamente.')