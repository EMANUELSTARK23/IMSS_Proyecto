# scripts/07_generar_html.py
from lxml import etree
import os

OUTPUT_XML = 'output/reporte_imss.xml'
OUTPUT_HTML = 'output/dashboard_imss.html'

# Le quitamos la 'b' del inicio para que Python acepte los acentos sin problemas
XSLT_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
  <html>
  <head>
    <title>Dashboard IMSS</title>
    <style>
      body { font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; }
      h1 { color: #1A56DB; }
      .resumen { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
      .badge { font-weight: bold; color: #E03C8A; }
    </style>
  </head>
  <body>
    <h1><xsl:value-of select="reporte_imss/metadatos/titulo"/></h1>
    
    <div class="resumen">
      <h2>Resumen Ejecutivo</h2>
      <ul>
        <li>Estado con más asegurados: <span class="badge"><xsl:value-of select="reporte_imss/resumen_ejecutivo/estado_mas_asegurados_2024"/></span></li>
        <li>Porcentaje de Mujeres: <span class="badge"><xsl:value-of select="reporte_imss/resumen_ejecutivo/porcentaje_mujeres_nacional"/></span></li>
        <li>Región con Mayor Masa Salarial: <span class="badge"><xsl:value-of select="reporte_imss/resumen_ejecutivo/region_mayor_masa_salarial"/></span></li>
        <li>Mayor Crecimiento (2015-2024): <span class="badge"><xsl:value-of select="reporte_imss/resumen_ejecutivo/estado_mayor_crecimiento_15_24"/></span></li>
      </ul>
    </div>
    
  </body>
  </html>
</xsl:template>
</xsl:stylesheet>
"""

def generar_html():
    # Cargar el XML y la plantilla (Añadimos .encode('utf-8') aquí)
    dom = etree.parse(OUTPUT_XML)
    xslt = etree.XML(XSLT_CONTENT.encode('utf-8'))
    transform = etree.XSLT(xslt)
    
    # Transformar y guardar
    newdom = transform(dom)
    with open(OUTPUT_HTML, 'wb') as f:
        f.write(etree.tostring(newdom, pretty_print=True, encoding="UTF-8"))
    
    print(f"¡Éxito! Reporte web generado en: {OUTPUT_HTML}")

if __name__ == '__main__':
    generar_html()