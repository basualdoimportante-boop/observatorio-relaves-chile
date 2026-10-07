# ============================================================
# EXPLORAR LOS TRES ARCHIVOS CSV DESCARGADOS
# ============================================================

import pandas as pd
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"

archivos = {
    "geoquimica": "live_geoquimica.csv",
    "otras_mediciones": "live_otras_mediciones.csv",
    "catastro": "live_catastro.csv",
}

for nombre, archivo in archivos.items():
    ruta = os.path.join(DATA_DIR, archivo)
    
    print("=" * 70)
    print(f"ARCHIVO: {nombre.upper()} ({archivo})")
    print("=" * 70)
    
    try:
        df = pd.read_csv(ruta)
        print(f"\nDimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        
        print(f"\nPrimeras 5 columnas:")
        for i, col in enumerate(df.columns[:10], 1):
            print(f"  {i}. {col}")
        if len(df.columns) > 10:
            print(f"  ... y {len(df.columns) - 10} columnas mas")
        
        # Verificar si existe la columna ID
        if "ID" in df.columns:
            print(f"\nColumna 'ID' presente. Valores unicos: {df['ID'].nunique()}")
            print(f"Rango de ID: {df['ID'].min()} a {df['ID'].max()}")
            print(f"Ejemplo de IDs: {df['ID'].head(5).tolist()}")
        else:
            print(f"\nNo hay columna 'ID'. Columnas disponibles: {df.columns.tolist()[:15]}")
        
        print()
    
    except Exception as e:
        print(f"  Error al leer: {e}\n")

print("=" * 70)
print("FIN DE LA EXPLORACION")
print("=" * 70)