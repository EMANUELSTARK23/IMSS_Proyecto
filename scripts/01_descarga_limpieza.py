# scripts/01_descarga_limpieza.py 
# Exploración y limpieza del dataset IMSS desde archivo local

import pandas as pd 
import os 
from dotenv import load_dotenv 

load_dotenv() 

CSV_CRUDO  = 'data.csv' 
CSV_LIMPIO = 'data/imss_asegurados_limpio.csv' 

def explorar_dataset(path: str) -> pd.DataFrame: 
    """Carga y muestra información básica del dataset""" 
    df = pd.read_csv(path, encoding='utf-8') 
    print(f'\n{"="*55}') 
    print(f'Forma del dataset: {df.shape[0]:,} filas x {df.shape[1]} columnas') 
    print(f'Columnas: {list(df.columns)}') 
    print(f'\nPrimeras 3 filas:') 
    print(df.head(3).to_string()) 
    print(f'\nTipos de datos:') 
    print(df.dtypes) 
    print(f'\nValores nulos por columna:') 
    print(df.isnull().sum()) 
    
    # CORRECCIÓN: Usar el nombre de columna real 'TOTAL'
    print(f'\nEstadísticas del campo TOTAL:') 
    print(df['TOTAL'].describe()) 
    return df 

def limpiar_dataset(df: pd.DataFrame) -> pd.DataFrame: 
    """Limpia y normaliza el dataset del IMSS""" 
    print(f'\nIniciando limpieza de {len(df):,} registros...') 

    # 1. Pasar todas las columnas a minúsculas para trabajar más fácil
    df.columns = df.columns.str.lower()

    # 2. Renombrar las columnas para que coincidan con tu lógica original
    df = df.rename(columns={ 
        'total':                 'total_asegurados', 
        'permanentes_del_campo': 'permanentes_campo', 
        'eventuales_del_campo':  'eventuales_campo', 
    }) 

    # 3. Mapear claves numéricas a texto (Catálogos del IMSS)
    diccionario_estados = {
        1: 'Aguascalientes', 2: 'Baja California', 3: 'Baja California Sur', 4: 'Campeche',
        5: 'Coahuila', 6: 'Colima', 7: 'Chiapas', 8: 'Chihuahua', 9: 'Ciudad De Mexico',
        10: 'Durango', 11: 'Guanajuato', 12: 'Guerrero', 13: 'Hidalgo', 14: 'Jalisco',
        15: 'Estado De Mexico', 16: 'Michoacan', 17: 'Morelos', 18: 'Nayarit',
        19: 'Nuevo Leon', 20: 'Oaxaca', 21: 'Puebla', 22: 'Queretaro', 23: 'Quintana Roo',
        24: 'San Luis Potosi', 25: 'Sinaloa', 26: 'Sonora', 27: 'Tabasco', 28: 'Tamaulipas',
        29: 'Tlaxcala', 30: 'Veracruz', 31: 'Yucatan', 32: 'Zacatecas'
    }
    df['entidad'] = df['cve_ent'].map(diccionario_estados)
    
    # El IMSS usa 1 para Hombre y 2 para Mujer
    df['sexo'] = df['sexo'].map({1: 'Hombre', 2: 'Mujer'})

    # 4. Eliminar filas con nulos en campos clave 
    antes = len(df) 
    df = df.dropna(subset=['periodo','entidad','sexo','total_asegurados']) 
    print(f'  Filas eliminadas por nulos: {antes - len(df)}') 

    # 5. Convertir 'periodo' a datetime y extraer año y mes 
    df['periodo'] = pd.to_datetime(df['periodo'], format='%Y-%m') 
    df['anio']    = df['periodo'].dt.year 
    df['mes']     = df['periodo'].dt.month 

    # 6. Asegurar tipos numéricos correctos 
    cols_int = ['total_asegurados','permanentes_urbanos', 
                'permanentes_campo','eventuales_urbanos','eventuales_campo'] 
    for col in cols_int: 
        if col in df.columns: 
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int) 

    # 7. Filtrar solo registros con asegurados positivos 
    df = df[df['total_asegurados'] > 0] 

    # 8. Agregar región geográfica 
    norte = ['Baja California','Baja California Sur','Sonora','Chihuahua', 
             'Coahuila','Nuevo Leon','Tamaulipas','Sinaloa','Durango'] 
    centro = ['Jalisco','Guanajuato','Michoacan','Queretaro','Aguascalientes', 
              'Colima','Nayarit','San Luis Potosi','Zacatecas','Hidalgo', 
              'Ciudad De Mexico','Estado De Mexico','Morelos','Tlaxcala','Puebla'] 
    df['region'] = df['entidad'].apply( 
        lambda x: 'Norte' if x in norte 
        else ('Centro' if x in centro else 'Sur-Sureste') 
    ) 

    print(f'  Registros tras limpieza: {len(df):,}') 
    print(f'  Entidades únicas: {df["entidad"].nunique()}') 
    print(f'  Años disponibles: {df["anio"].min()} – {df["anio"].max()}') 
    print(f'  Regiones: {df["region"].value_counts().to_dict()}') 
    return df 

if __name__ == '__main__': 
    df = explorar_dataset(CSV_CRUDO) 
    df_limpio = limpiar_dataset(df) 
    
    os.makedirs('data', exist_ok=True)
    df_limpio.to_csv(CSV_LIMPIO, index=False, encoding='utf-8') 
    
    print(f'\nDataset limpio guardado en: {CSV_LIMPIO}') 
    print('Exploración y limpieza completadas con éxito.')