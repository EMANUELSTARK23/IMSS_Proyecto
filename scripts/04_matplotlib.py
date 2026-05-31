# scripts/04_matplotlib.py 
# Visualizaciones con Matplotlib — datos IMSS desde MongoDB 
  
import matplotlib.pyplot as plt 
import pandas as pd  # Importado para el Desafío 1
import os 
from dotenv import load_dotenv 
import importlib

# ── Truco para importar archivos que empiezan con número ──
pipelines = importlib.import_module("03_pipelines")

# Extraemos las funciones que necesitamos del módulo cargado
conectar_local = pipelines.conectar_local
p1_por_entidad = pipelines.p1_por_entidad
p2_evolucion_temporal = pipelines.p2_evolucion_temporal
p3_por_sexo = pipelines.p3_por_sexo
p4_tipo_trabajador = pipelines.p4_tipo_trabajador
p5_por_region = pipelines.p5_por_region
  
load_dotenv() 
OUTPUT = 'output/graficas' 
os.makedirs(OUTPUT, exist_ok=True) 
  
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False}) 
FUENTE = 'Fuente: IMSS / datamx.io (CC Zero)' 
  
# ── Gráfica 1: Barras horizontales — Top entidades 2024 ───── 
def g1_top_entidades(col): 
    datos     = p1_por_entidad(col, anio=2024) 
    entidades = [d['_id'] for d in datos] 
    totales   = [d['total']/1e6 for d in datos] 
  
    fig, ax = plt.subplots(figsize=(12, 10)) 
    bars = ax.barh(entidades, totales, color='#1A56DB', edgecolor='white') 
    ax.set_xlabel('Trabajadores asegurados (millones)', fontsize=12) 
    ax.set_title('Trabajadores Asegurados por Entidad Federativa — 2024\n(IMSS / datamx.io)', 
                 fontsize=14, fontweight='bold', pad=15) 
    ax.bar_label(bars, fmt='%.1fM', padding=4, fontsize=9) 
    ax.invert_yaxis() 
    fig.text(0.99, 0.01, FUENTE, ha='right', fontsize=8, color='gray') 
    plt.tight_layout() 
    plt.savefig(f'{OUTPUT}/01_top_entidades_2024.png', dpi=150, bbox_inches='tight') 
    print('  01_top_entidades_2024.png') 
    plt.close() 
  
# ── Gráfica 2: Línea — Evolución temporal 1997-2026 ───────── 
def g2_evolucion(col): 
    datos = p2_evolucion_temporal(col) 
    # Filtrar desde 2010 para mejor visualización 
    datos = [d for d in datos if d['anio'] >= 2010] 
    x = [f"{d['anio']}-{d['mes']:02d}" for d in datos] 
    y = [d['total']/1e6 for d in datos] 
  
    fig, ax = plt.subplots(figsize=(14, 5)) 
    ax.plot(x, y, color='#1A56DB', linewidth=2.5, marker='o', markersize=2) 
    ax.fill_between(x, y, alpha=0.1, color='#1A56DB') 
    
    # DESAFÍO 2: Marcar el impacto del COVID-19 con un rectángulo sombreado
    ax.axvspan('2020-03', '2020-12', color='red', alpha=0.2, label='Impacto COVID-19') 
    
    ax.legend(fontsize=10) 
    ax.set_title('Evolución Mensual de Trabajadores Asegurados (Nacional)\n2010-2026', 
                 fontsize=14, fontweight='bold') 
    ax.set_ylabel('Millones de asegurados') 
    tick_pos = list(range(0, len(x), 12)) 
    ax.set_xticks(tick_pos) 
    ax.set_xticklabels([x[i] for i in tick_pos], rotation=45, ha='right') 
    fig.text(0.99, 0.01, FUENTE, ha='right', fontsize=8, color='gray') 
    plt.tight_layout() 
    plt.savefig(f'{OUTPUT}/02_evolucion_temporal.png', dpi=150, bbox_inches='tight') 
    print('  02_evolucion_temporal.png') 
    plt.close() 
  
# ── Gráfica 3: Pastel — Distribución por sexo ─────────────── 
def g3_por_sexo(col): 
    datos  = p3_por_sexo(col) 
    labels = [d['_id'] for d in datos] 
    sizes  = [d['total'] for d in datos] 
    colors = ['#1A56DB','#E03C8A'] 
  
    fig, ax = plt.subplots(figsize=(7, 7)) 
    wedges, texts, autotexts = ax.pie( 
        sizes, labels=labels, colors=colors, 
        autopct='%1.1f%%', startangle=90, 
        wedgeprops={'edgecolor':'white','linewidth':2} 
    ) 
    for at in autotexts: at.set_fontsize(13) 
    ax.set_title('Distribución de Asegurados por Sexo\n(Acumulado 1997-2026)', 
                 fontsize=14, fontweight='bold') 
    fig.text(0.99, 0.01, FUENTE, ha='right', fontsize=8, color='gray') 
    plt.tight_layout() 
    plt.savefig(f'{OUTPUT}/03_por_sexo.png', dpi=150, bbox_inches='tight') 
    print('  03_por_sexo.png') 
    plt.close() 
  
# ── Gráfica 4: Barras — Tipo de trabajador 2024 ───────────── 
def g4_tipo_trabajador(col): 
    datos  = p4_tipo_trabajador(col, anio=2024)[0] 
    cats   = ['Permanentes\nUrbanos','Permanentes\nCampo', 
              'Eventuales\nUrbanos','Eventuales\nCampo'] 
    vals   = [datos['perm_urbanos']/1e6, datos['perm_campo']/1e6, 
              datos['even_urbanos']/1e6, datos['even_campo']/1e6] 
    colors = ['#1A56DB','#3B82F6','#EA580C','#F97316'] 
  
    fig, ax = plt.subplots(figsize=(10, 6)) 
    bars = ax.bar(cats, vals, color=colors, edgecolor='white', width=0.6) 
    ax.set_title('Trabajadores Asegurados por Tipo — 2024', 
                 fontsize=14, fontweight='bold') 
    ax.set_ylabel('Millones de trabajadores') 
    ax.bar_label(bars, fmt='%.1fM', padding=4, fontsize=11) 
    fig.text(0.99, 0.01, FUENTE, ha='right', fontsize=8, color='gray') 
    plt.tight_layout() 
    plt.savefig(f'{OUTPUT}/04_tipo_trabajador_2024.png', dpi=150, bbox_inches='tight') 
    print('  04_tipo_trabajador_2024.png') 
    plt.close() 

# ── DESAFÍO 1: Gráfica 5: Barras Apiladas (Top 10 Entidades por Sexo) ──
def g5_barras_apiladas(col):
    # Primero obtenemos el top 10 general
    top_10 = list(col.aggregate([
        { '$match': { 'anio': 2024 } },
        { '$group': { '_id': '$entidad', 'total': { '$sum': '$total_asegurados' } } },
        { '$sort': { 'total': -1 } },
        { '$limit': 10 }
    ]))
    top_10_entidades = [d['_id'] for d in top_10]

    # Luego sacamos los datos divididos por sexo solo para esas 10 entidades
    datos = list(col.aggregate([
        { '$match': { 'anio': 2024, 'entidad': { '$in': top_10_entidades } } },
        { '$group': {
            '_id': { 'entidad': '$entidad', 'sexo': '$sexo' },
            'total': { '$sum': '$total_asegurados' }
        }}
    ]))

    # Preparamos los datos con Pandas para apilarlos fácilmente
    df = pd.DataFrame([{
        'entidad': d['_id']['entidad'],
        'sexo': d['_id']['sexo'],
        'total': d['total'] / 1e6
    } for d in datos])

    pivot_df = df.pivot(index='entidad', columns='sexo', values='total').reindex(top_10_entidades)

    fig, ax = plt.subplots(figsize=(12, 7))
    pivot_df.plot(kind='bar', stacked=True, color=['#1A56DB', '#E03C8A'], ax=ax, edgecolor='white')

    ax.set_title('Top 10 Entidades por Sexo — 2024 (Barras Apiladas)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Millones de asegurados')
    ax.set_xlabel('Entidad Federativa')
    plt.xticks(rotation=45, ha='right')
    ax.legend(title='Sexo')
    
    fig.text(0.99, 0.01, FUENTE, ha='right', fontsize=8, color='gray')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT}/05_barras_apiladas_sexo_2024.png', dpi=150, bbox_inches='tight')
    print('  05_barras_apiladas_sexo_2024.png')
    plt.close()
  
if __name__ == '__main__': 
    print('Generando visualizaciones con Matplotlib...') 
    col = conectar_local() 
    g1_top_entidades(col) 
    g2_evolucion(col) 
    g3_por_sexo(col) 
    g4_tipo_trabajador(col) 
    g5_barras_apiladas(col)  # Llamada a la nueva gráfica
    print('\n5 gráficas matplotlib guardadas en output/graficas/')