# scripts/06_exportar_xml.py 
# Exportación de resultados de MongoDB a XML validado con XSD 
  
from lxml import etree 
from pymongo import MongoClient 
from datetime import datetime 
from dotenv import load_dotenv 
import os, glob 
import importlib

# ── Truco para importar archivos que empiezan con número ──
pipelines = importlib.import_module("03_pipelines")
conectar_local = pipelines.conectar_local
p1_por_entidad = pipelines.p1_por_entidad
p2_evolucion_temporal = pipelines.p2_evolucion_temporal
p3_por_sexo = pipelines.p3_por_sexo
p4_tipo_trabajador = pipelines.p4_tipo_trabajador
p5_por_region = pipelines.p5_por_region
p6_top_crecimiento = pipelines.p6_top_crecimiento
  
load_dotenv() 
OUTPUT_XML = 'output/reporte_imss.xml' 
URL_DATASET = os.getenv('DATASET_URL', 
    'https://datamx.io/dataset/trabajadores-permanentes-y-eventuales' 
    '-asegurados-en-el-imss-en-mexico-por-entidad-1997-2025' 
    '/resource/382fbd94-4047-437d-9c59-54cd601dfa33') 
  
def construir_xml(resultados: dict, total_docs: int) -> etree._Element: 
    raiz = etree.Element('reporte_imss') 
  
    # ── Metadatos ────────────────────────────────────────── 
    meta = etree.SubElement(raiz, 'metadatos') 
    etree.SubElement(meta,'titulo').text = 'Análisis de Empleo Formal en México — IMSS 1997-2026'
    etree.SubElement(meta,'fuente').text = 'IMSS / datamx.io (CC Zero)' 
    etree.SubElement(meta,'url_dataset').text = URL_DATASET 
    etree.SubElement(meta,'fecha_generacion').text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    etree.SubElement(meta,'total_documentos').text = str(total_docs) 
  
    graficas_el = etree.SubElement(meta,'graficas') 
    for png in sorted(glob.glob('output/graficas/*.png')): 
        g = etree.SubElement(graficas_el,'grafica') 
        g.set('ruta', png) 
        g.set('nombre', os.path.basename(png)) 
  
    # ── Resultados ───────────────────────────────────────── 
    res_el = etree.SubElement(raiz,'resultados') 
  
    # P1 — Por entidad 
    p = etree.SubElement(res_el,'pipeline') 
    p.set('nombre','por_entidad_2024') 
    for d in resultados['p1']: 
        el = etree.SubElement(p,'entidad') 
        el.set('nombre', str(d['_id'])) 
        el.set('total',  str(d['total'])) 
  
    # P2 — Evolución temporal (primeros y últimos 6 meses) 
    p = etree.SubElement(res_el,'pipeline') 
    p.set('nombre','evolucion_temporal') 
    datos_t = resultados['p2'] 
    muestra = datos_t[:6] + datos_t[-6:] 
    for d in muestra: 
        el = etree.SubElement(p,'periodo') 
        el.set('anio', str(d['anio'])) 
        el.set('mes',  str(d['mes'])) 
        el.set('total', str(d['total'])) 
  
    # P3 — Por sexo 
    p = etree.SubElement(res_el,'pipeline') 
    p.set('nombre','por_sexo') 
    for d in resultados['p3']: 
        el = etree.SubElement(p,'grupo') 
        el.set('sexo',    str(d['_id'])) 
        el.set('total',   str(d['total'])) 
        el.set('promedio', f"{d['promedio']:.2f}") 
  
    # P4 — Tipo de trabajador 
    p = etree.SubElement(res_el,'pipeline') 
    p.set('nombre','tipo_trabajador_2024') 
    if resultados['p4']: 
        d = resultados['p4'][0] 
        for campo in ['perm_urbanos','perm_campo','even_urbanos','even_campo']: 
            el = etree.SubElement(p,'tipo') 
            el.set('categoria', campo) 
            el.set('total', str(d.get(campo, 0))) 
  
    # P5 — Por región 
    p = etree.SubElement(res_el,'pipeline') 
    p.set('nombre','por_region_2024') 
    for d in resultados['p5']: 
        el = etree.SubElement(p,'region') 
        el.set('nombre', str(d['_id'])) 
        el.set('total',  str(d['total'])) 
        el.set('masa_salarial', f"{d['masa_salarial']:.2f}") 
  
    # P6 — Top crecimiento 
    p = etree.SubElement(res_el,'pipeline') 
    p.set('nombre','top_crecimiento_2015_2024') 
    for d in resultados['p6']: 
        el = etree.SubElement(p,'entidad') 
        el.set('nombre',      str(d['_id'])) 
        el.set('crecimiento', str(d.get('crecimiento_abs',0))) 
  
    return raiz 
  
def guardar_xml(raiz, ruta): 
    tree = etree.ElementTree(raiz) 
    etree.indent(tree, space='  ') 
    with open(ruta,'wb') as f: 
        tree.write(f, xml_declaration=True, encoding='UTF-8', pretty_print=True) 
    print(f'  XML guardado: {ruta}') 
    print(f'  Tamaño: {os.path.getsize(ruta):,} bytes') 
  
def validar_xml(ruta_xml, ruta_xsd): 
    try: 
        schema = etree.XMLSchema(etree.parse(ruta_xsd)) 
        if schema.validate(etree.parse(ruta_xml)): 
            print('  XML válido según el esquema XSD') 
        else: 
            for e in schema.error_log: 
                print(f'  {e.message}') 
    except Exception as e: 
        print(f'   No se pudo validar: {e}') 
  
if __name__ == '__main__': 
    col = conectar_local() 
    total_docs = col.count_documents({}) 
    print(f'Total documentos en MongoDB: {total_docs:,}') 
    print('Ejecutando pipelines...') 
    resultados = { 
        'p1': p1_por_entidad(col), 
        'p2': p2_evolucion_temporal(col), 
        'p3': p3_por_sexo(col), 
        'p4': p4_tipo_trabajador(col), 
        'p5': p5_por_region(col), 
        'p6': p6_top_crecimiento(col), 
    } 
    print('Construyendo XML...') 
    raiz = construir_xml(resultados, total_docs) 
    os.makedirs('output', exist_ok=True) 
    guardar_xml(raiz, OUTPUT_XML) 
    validar_xml(OUTPUT_XML, 'scripts/reporte_imss.xsd') 
    print('\nExportación XML completada.')