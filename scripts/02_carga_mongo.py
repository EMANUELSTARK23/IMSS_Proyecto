# scripts/02_carga_mongo.py 
# Carga del dataset IMSS a MongoDB local y Atlas con pymongo 
  
import pandas as pd 
from pymongo import MongoClient, ASCENDING 
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
  
def cargar_coleccion(client: MongoClient, db_name: str, 
                     col_name: str, docs: list) -> None: 
    db  = client[db_name] 
    col = db[col_name] 
  
    # Limpiar datos previos 
    eliminados = col.delete_many({}).deleted_count 
    print(f'   Documentos previos eliminados: {eliminados:,}') 
  
    # Insertar en lotes de 5,000 
    LOTE = 5000 
    insertados = 0 
    for i in range(0, len(docs), LOTE): 
        lote = docs[i:i+LOTE] 
        resultado = col.insert_many(lote, ordered=False) 
        insertados += len(resultado.inserted_ids) 
        pct = (i + len(lote)) / len(docs) * 100 
        print(f'  ⬆  {pct:.0f}% — {insertados:,} documentos insertados', end='\r') 
    print(f'  Total insertados: {insertados:,}        ') 
  
    # Crear índices para optimizar los pipelines 
    col.create_index([('entidad', ASCENDING)]) 
    col.create_index([('anio', ASCENDING), ('mes', ASCENDING)]) 
    col.create_index([('region', ASCENDING)]) 
    col.create_index([('sector_1', ASCENDING)]) 
    col.create_index([('sexo', ASCENDING)]) 
    print(f'   Índices creados: entidad, anio+mes, region, sector_1, sexo') 
  
if __name__ == '__main__': 
    docs = csv_a_documentos(CSV_PATH) 
  
    print('\n── Cargando a MongoDB LOCAL ──') 
    cl = conectar(MONGO_LOCAL_URI, 'MongoDB Local') 
    cargar_coleccion(cl, MONGO_LOCAL_DB, COLECCION, docs) 
    cl.close() 
  
    print('\n── Cargando a MongoDB ATLAS ──') 
    ca = conectar(MONGO_ATLAS_URI, 'MongoDB Atlas') 
    cargar_coleccion(ca, MONGO_ATLAS_DB, COLECCION, docs) 
    ca.close() 
  
    print('\nCarga completada en ambas instancias.') 