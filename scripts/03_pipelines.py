# scripts/03_pipelines.py 
# Aggregation Pipelines del IMSS ejecutados desde Python con pymongo 

from pymongo import MongoClient 
from dotenv import load_dotenv 
import pandas as pd  # Agregado para el Desafío 1
import sys           # Agregado para el Desafío 2
import os 

load_dotenv() 

def conectar_local(): 
    client = MongoClient(os.getenv('MONGO_LOCAL_URI')) 
    return client[os.getenv('MONGO_LOCAL_DB')][os.getenv('COLECCION')] 

def conectar_atlas(): 
    client = MongoClient(os.getenv('MONGO_ATLAS_URI')) 
    return client[os.getenv('MONGO_ATLAS_DB')][os.getenv('COLECCION')] 

# Pipeline 1 — Top entidades por asegurados 
def p1_por_entidad(col, anio) -> list: 
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

# Pipeline 4 — Tipo de trabajador 
def p4_tipo_trabajador(col, anio) -> list: 
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
def p5_por_region(col, anio) -> list: 
    return list(col.aggregate([ 
        { '$match': { 'anio': anio } }, 
        { '$group': { 
            '_id': '$region', 
            'total': { '$sum': '$total_asegurados' }, 
            'masa_salarial': { '$sum': '$masa_salarial_total' } 
        }}, 
        { '$sort': { 'total': -1 } } 
    ])) 

# Pipeline 6 — Top crecimiento (2015 vs el año ingresado)
def p6_top_crecimiento(col, anio) -> list: 
    return list(col.aggregate([ 
        { '$match': { 'anio': { '$in': [2015, anio] } } }, 
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

# DESAFÍO 1: Pipeline 7 — Salario promedio por trabajador 
def p7_salario_promedio(col, anio) -> list:
    return list(col.aggregate([
        { '$match': { 'anio': anio } },
        { '$group': { 
            '_id': '$entidad', 
            'salario_promedio': { 
                '$avg': { '$divide': ['$masa_salarial_total', '$total_asegurados'] } 
            } 
        }},
        { '$sort': { 'salario_promedio': -1 } }
    ]))


if __name__ == '__main__': 
    # DESAFÍO 2: Recibir el año como argumento desde la terminal (por defecto 2024 si no se pone nada)
    anio_filtro = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    
    col = conectar_local() 
    print(f'\n── Ejecutando pipelines para el año {anio_filtro} ──')
    
    pipelines = { 
        f'P1 — Por entidad ({anio_filtro})':    p1_por_entidad(col, anio_filtro), 
        'P2 — Evolución temporal':              p2_evolucion_temporal(col), 
        'P3 — Por sexo':                        p3_por_sexo(col), 
        f'P4 — Tipo trabajador ({anio_filtro})':p4_tipo_trabajador(col, anio_filtro), 
        f'P5 — Por región ({anio_filtro})':     p5_por_region(col, anio_filtro), 
        f'P6 — Top crecimiento (2015 vs {anio_filtro})': p6_top_crecimiento(col, anio_filtro), 
    } 
    
    for nombre, datos in pipelines.items(): 
        print(f'\n── {nombre} ({len(datos)} resultados) ──') 
        # Imprime solo los primeros 3 resultados de cada pipeline
        for fila in datos[:3]: 
            print(f'   {fila}') 
            
    # Mostrar el Pipeline 7 en formato Pandas DataFrame
    print(f'\n── P7 — Salario Promedio por Entidad ({anio_filtro}) (Desafío Pandas) ──')
    datos_p7 = p7_salario_promedio(col, anio_filtro)
    df_salario = pd.DataFrame(datos_p7)
    df_salario.rename(columns={'_id': 'Entidad', 'salario_promedio': 'Salario Promedio'}, inplace=True)
    print(df_salario.head()) # Imprime los primeros 5 resultados como tabla
            
    print('\nPipelines ejecutados correctamente.')