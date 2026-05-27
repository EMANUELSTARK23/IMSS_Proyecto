# scripts/05_seaborn.py 
# Visualizaciones estadísticas avanzadas con Seaborn — datos IMSS 
  
import seaborn as sns 
import matplotlib.pyplot as plt 
import pandas as pd 
from pymongo import MongoClient 
from dotenv import load_dotenv 
import os 
  
load_dotenv() 
OUTPUT = 'output/graficas' 
os.makedirs(OUTPUT, exist_ok=True) 
  
sns.set_theme(style='whitegrid', palette='Blues_d') 
FUENTE = 'Fuente: IMSS / datamx.io (CC Zero)' 
  
def obtener_df(filtro_anio=None): 
    """Carga datos desde MongoDB local a un DataFrame de pandas""" 
    client = MongoClient(os.getenv('MONGO_LOCAL_URI')) 
    col = client[os.getenv('MONGO_LOCAL_DB')][os.getenv('COLECCION')] 
    query = {'anio': {'$gte': filtro_anio}} if filtro_anio else {} 
    datos = list(col.find(query, {'_id':0})) 
    df = pd.DataFrame(datos) 
    client.close() 
    return df 
  
# ── Gráfica 5: Heatmap — asegurados por entidad y año ─────── 
def g5_heatmap(df): 
    # Agrupar por entidad y año — solo últimos 10 años 
    df_rec = df[df['anio'] >= 2014] 
    pivot = df_rec.groupby(['entidad','anio'])['total_asegurados'].sum().unstack() 
    pivot = pivot / 1e6 
  
    fig, ax = plt.subplots(figsize=(12, 14)) 
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd', 
                linewidths=0.5, ax=ax, cbar_kws={'label':'Millones'}) 
    ax.set_title('Trabajadores Asegurados por Entidad y Año (millones)\n2014-2024', 
                 fontsize=13, fontweight='bold', pad=15) 
    ax.set_xlabel('Año') 
    ax.set_ylabel('Entidad Federativa') 
    fig.text(0.99, 0.01, FUENTE, ha='right', fontsize=8, color='gray') 
    plt.tight_layout() 
    plt.savefig(f'{OUTPUT}/05_heatmap_entidad_anio.png', dpi=150, bbox_inches='tight') 
    print('  05_heatmap_entidad_anio.png') 
    plt.close() 
  
# ── Gráfica 6: Boxplot — distribución por región ───────────── 
def g6_boxplot_region(df): 
    df_2024 = df[df['anio'] == 2024].copy() 
    df_2024['asegurados_m'] = df_2024['total_asegurados'] / 1e3 
  
    fig, ax = plt.subplots(figsize=(10, 6)) 
    sns.boxplot( 
        data=df_2024, x='region', y='asegurados_m', 
        palette={'Norte':'#1A56DB','Centro':'#16A34A','Sur-Sureste':'#EA580C'}, 
        ax=ax, linewidth=1.5 
    ) 
    ax.set_title('Distribución de Asegurados por Región — 2024', 
                 fontsize=14, fontweight='bold') 
    ax.set_xlabel('Región') 
    ax.set_ylabel('Asegurados (miles)') 
    fig.text(0.99, 0.01, FUENTE, ha='right', fontsize=8, color='gray') 
    plt.tight_layout() 
    plt.savefig(f'{OUTPUT}/06_boxplot_region_2024.png', dpi=150, bbox_inches='tight') 
    print('  06_boxplot_region_2024.png') 
    plt.close() 
  
# ── Gráfica 7: Barplot — por sexo y región 2024 ───────────── 
def g7_barplot_sexo_region(df): 
    df_2024 = df[df['anio'] == 2024] 
    res = df_2024.groupby(['region','sexo'])['total_asegurados'].sum().reset_index() 
    res['asegurados_m'] = res['total_asegurados'] / 1e6 
  
    fig, ax = plt.subplots(figsize=(10, 6)) 
    sns.barplot(data=res, x='region', y='asegurados_m', 
                hue='sexo', palette=['#1A56DB','#E03C8A'], ax=ax) 
    ax.set_title('Asegurados por Región y Sexo — 2024', 
                 fontsize=14, fontweight='bold') 
    ax.set_xlabel('Región') 
    ax.set_ylabel('Asegurados (millones)') 
    ax.legend(title='Sexo') 
    fig.text(0.99, 0.01, FUENTE, ha='right', fontsize=8, color='gray') 
    plt.tight_layout() 
    plt.savefig(f'{OUTPUT}/07_barplot_sexo_region_2024.png', dpi=150, bbox_inches='tight') 
    print('  07_barplot_sexo_region_2024.png') 
    plt.close() 
  
# ── Gráfica 8: Lineplot con bandas — evolución por región ──── 
def g8_lineplot_region(df): 
    df_rec = df[df['anio'] >= 2010] 
    res = df_rec.groupby(['anio','region'])['total_asegurados'].sum().reset_index() 
    res['total_m'] = res['total_asegurados'] / 1e6 
  
    fig, ax = plt.subplots(figsize=(13, 6)) 
    sns.lineplot( 
        data=res, x='anio', y='total_m', hue='region', 
        palette={'Norte':'#1A56DB','Centro':'#16A34A','Sur-Sureste':'#EA580C'}, 
        marker='o', linewidth=2.5, ax=ax 
    ) 
    ax.axvline(x=2020, color='red', linestyle='--', alpha=0.4, label='COVID-19') 
    ax.set_title('Evolución de Asegurados por Región (2010-2024)', 
                 fontsize=14, fontweight='bold') 
    ax.set_xlabel('Año') 
    ax.set_ylabel('Asegurados (millones)') 
    ax.legend(title='Región') 
    fig.text(0.99, 0.01, FUENTE, ha='right', fontsize=8, color='gray') 
    plt.tight_layout() 
    plt.savefig(f'{OUTPUT}/08_lineplot_evolucion_region.png', dpi=150, bbox_inches='tight') 
    print('  08_lineplot_evolucion_region.png') 
    plt.close() 
  
if __name__ == '__main__': 
    print('Cargando datos desde MongoDB...') 
    df = obtener_df(filtro_anio=2010) 
    print(f'  DataFrame: {len(df):,} registros') 
    print('Generando visualizaciones con Seaborn...') 
    g5_heatmap(df) 
    g6_boxplot_region(df) 
    g7_barplot_sexo_region(df) 
    g8_lineplot_region(df) 
    print('\n4 gráficas seaborn guardadas en output/graficas/')