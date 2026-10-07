# ============================================================
# SCRIPT 02: DESCARGAR DATOS GEOQUÍMICOS DE SERNAGEOMIN
# Fuente: Servicio de características de ArcGIS
# ============================================================

import requests
import pandas as pd
import json

# 1. URL del servicio de ArcGIS
base_url = "https://services1.arcgis.com/OyivVdFT15hfsDx3/arcgis/rest/services/PLATAFORMA_PUBLICA_RELAVES_WFL1/FeatureServer"

# 2. Capa de geoquímica (Layer 25: GQ_RELAVES)
capa_geoquimica = 25

# 3. Construir la URL de consulta
#    - where=1=1: traer todos los registros
#    - outFields=*: todas las columnas
#    - f=json: formato de respuesta
#    - resultRecordCount: límite de registros (usamos un valor alto)
url_consulta = f"{base_url}/{capa_geoquimica}/query"
parametros = {
    "where": "1=1",
    "outFields": "*",
    "f": "json",
    "resultRecordCount": 10000,  # Más que suficiente para ~2000 muestras
    "returnGeometry": "false"    # No necesitamos geometría, solo datos
}

# 4. Hacer la consulta
print("Consultando el servicio de SERNAGEOMIN...")
respuesta = requests.get(url_consulta, params=parametros)

# 5. Verificar que la respuesta sea exitosa
if respuesta.status_code == 200:
    datos = respuesta.json()
    
    # Verificar si hay errores en la respuesta
    if "error" in datos:
        print(f"Error del servicio: {datos['error']}")
    else:
        # Extraer los registros
        registros = datos.get("features", [])
        print(f"Registros descargados: {len(registros)}")
        
        # Convertir a DataFrame
        df = pd.DataFrame([r["attributes"] for r in registros])
        
        # Mostrar información básica
        print(f"\nDimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"\nColumnas disponibles:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        # Guardar en CSV
        ruta_salida = r"C:\Users\Martín\Desktop\RELAVES\data\geoquimica_relaves.csv"
        df.to_csv(ruta_salida, index=False, encoding="utf-8")
        print(f"\nArchivo guardado en: {ruta_salida}")
        
else:
    print(f"Error en la consulta: {respuesta.status_code}")
    print(respuesta.text[:500])
    