# Análisis de Datos IMSS con Python y MongoDB 
  
## Descripción 
Pipeline de análisis de empleo formal en México usando datos del IMSS. 
Fuente: datamx.io | Almacenamiento: MongoDB 8 | Viz: matplotlib + seaborn 
  
## Dataset 
Empleo formal en México: trabajadores asegurados en el IMSS (1997-2026) 
URL: https://datamx.io/dataset/trabajadores-permanentes-y-eventuales-... 
Licencia: Creative Commons CC Zero 
  
## Instalación 
python -m venv venv 
venv\Scripts\activate 
pip install -r requirements.txt 
# Editar .env con tus credenciales de MongoDB Atlas 
  
## Estructura 
data/          <- dataset CSV (ignorado por Git) 
scripts/       <- scripts Python por etapa 
output/        <- graficas PNG y reporte XML (ignorado por Git) 
requirements.txt 