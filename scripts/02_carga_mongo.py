# scripts/02_carga_mongo.py 
# Carga del dataset IMSS a MongoDB local y Atlas con pymongo 
  
import pandas as pd 
from pymongo import MongoClient, ASCENDING, UpdateOne 
from dotenv import load_dotenv 
import os 
  
load_dotenv() 
  
MONGO_LOCAL_URI = os.getenv('MONGO_LOCAL_URI') 
MONGO_ATLAS_URI = os.getenv('MONGO_ATLAS_URI') 
MONGO_LOCAL_DB  = os.getenv('MONGO_LOCAL_DB') 
MONGO_ATLAS_DB  = os.getenv('MONGO_ATLAS_DB') 
COLECCION       = os.getenv('COLECCION') 
CSV_PATH        = 'data/imss_asegurados_limpio.csv' 
  
def conectar(uri: str, nombre: str) -> MongoClient: 
    try: 
        client = MongoClient(uri, serverSelectionTimeoutMS=5000) 
        client.admin.command('ping') 
        print(f'Conexión exitosa a {nombre}') 
        return client 
    except Exception as e: 
        print(f'Error al conectar a {nombre}: {e}') 
        raise 
  
def csv_a_documentos(path: str) -> list: 
    """Convierte CSV limpio a lista de documentos MongoDB""" 
    df = pd.read_csv(path, encoding='utf-8') 
    df['periodo'] = pd.to_datetime(df['periodo']) 
    
    # Convertir columnas numéricas a int nativo de Python 
    cols_int = ['total_asegurados','permanentes_urbanos', 
                'permanentes_campo','eventuales_urbanos', 
                'eventuales_campo','anio','mes'] 
    for col in cols_int: 
        if col in df.columns: 
            df[col] = df[col].astype(int) 
            
    docs = df.to_dict(orient='records') 
    print(f' {len(docs):,} documentos preparados') 
    return docs 
  
def cargar_coleccion_upsert(client: MongoClient, db_name: str, 
                     col_name: str, docs: list) -> None: 
    db  = client[db_name] 
    col = db[col_name] 
  
    # DESAFÍO 1: Usar upsert en lugar de delete_many e insert_many
    print(f'   Iniciando carga con UPSERT (puede tardar más por la validación de duplicados)...') 
  
    # Insertar/Actualizar en lotes de 5,000 
    LOTE = 5000 
    procesados = 0 
    for i in range(0, len(docs), LOTE): 
        lote = docs[i:i+LOTE] 
        
        # Crear lista de operaciones UpdateOne usando la clave única solicitada
        # CORRECCIÓN: Usamos .get() para evitar el KeyError si la columna conservó su nombre original
        operaciones = [
            UpdateOne(
                {
                    'periodo': d['periodo'], 
                    'entidad': d['entidad'], 
                    'sexo': d['sexo'], 
                    'sector_1': d.get('sector_1', d.get('sector_economico_1'))
                },
                {'$set': d},
                upsert=True
            ) for d in lote
        ]
        
        col.bulk_write(operaciones, ordered=False) 
        procesados += len(lote) 
        pct = procesados / len(docs) * 100 
        print(f'  ⬆  {pct:.0f}% — {procesados:,} documentos procesados', end='\r') 
    print(f'\n  Total procesados (insertados/actualizados): {procesados:,}        ') 
  
    # Crear índices para optimizar los pipelines 
    col.create_index([('entidad', ASCENDING)]) 
    col.create_index([('anio', ASCENDING), ('mes', ASCENDING)]) 
    col.create_index([('region', ASCENDING)]) 
    col.create_index([('sector_1', ASCENDING)]) 
    col.create_index([('sexo', ASCENDING)]) 
    print(f'   Índices creados: entidad, anio+mes, region, sector_1, sexo') 

# DESAFÍO 2: Función de verificación y alerta
def verificar_sincronizacion(cl: MongoClient, ca: MongoClient, col_name: str):
    docs_local = cl[MONGO_LOCAL_DB][col_name].count_documents({})
    docs_atlas = ca[MONGO_ATLAS_DB][col_name].count_documents({})
    
    print('\n── Verificación de Sincronización ──')
    print(f'Documentos en Local: {docs_local:,}')
    print(f'Documentos en Atlas: {docs_atlas:,}')
    
    if docs_local == docs_atlas:
        print('✅ ¡Éxito! Ambas bases de datos están sincronizadas.')
    else:
        print('⚠️ ¡ALERTA! Hay una diferencia en la cantidad de documentos entre Local y Atlas.')
  
if __name__ == '__main__': 
    docs = csv_a_documentos(CSV_PATH) 
  
    print('\n── Cargando a MongoDB LOCAL ──') 
    cl = conectar(MONGO_LOCAL_URI, 'MongoDB Local') 
    cargar_coleccion_upsert(cl, MONGO_LOCAL_DB, COLECCION, docs) 
    
    print('\n── Cargando a MongoDB ATLAS ──') 
    ca = conectar(MONGO_ATLAS_URI, 'MongoDB Atlas') 
    cargar_coleccion_upsert(ca, MONGO_ATLAS_DB, COLECCION, docs) 
  
    # Ejecutar el Desafío 2 (Comparación Local vs Atlas)
    verificar_sincronizacion(cl, ca, COLECCION)

    cl.close() 
    ca.close() 
    print('\nCarga completada en ambas instancias.')