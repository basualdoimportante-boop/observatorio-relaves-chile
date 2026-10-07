# ============================================================
# EXPLORAR MAPA DE AMENAZA SISMICA
# ============================================================

import pandas as pd
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"

print("=" * 70)
print("EXPLORACION DEL MAPA DE AMENAZA SISMICA")
print("=" * 70)

# Cargar solo las primeras filas para no saturar memoria
ruta = os.path.join(DATA_DIR, "mapa_amenaza.csv")

# Primero, leer solo las primeras 5 filas para ver estructura
df_head = pd.read_csv(ruta, nrows=5)
print(f"\n--- Primeras 5 filas ---")
print(df_head.to_string())

print(f"\n--- Columnas ---")
for i, col in enumerate(df_head.columns, 1):
    print(f"  {i}. {col}")

print(f"\n--- Tipos de datos ---")
print(df_head.dtypes)

# Contar total de filas (leyendo solo la primera columna)
print(f"\n--- Contando filas totales ---")
df_full = pd.read_csv(ruta)
print(f"  Total de filas: {len(df_full):,}")
print(f"  Total de columnas: {df_full.shape[1]}")

# Estadisticas basicas
print(f"\n--- Estadisticas basicas ---")
print(df_full.describe().to_string())

# Ver rangos geograficos (si hay columnas de lat/lon)
columnas_posibles_lat = [c for c in df_full.columns if "lat" in c.lower()]
columnas_posibles_lon = [c for c in df_full.columns if "lon" in c.lower()]

if columnas_posibles_lat and columnas_posibles_lon:
    lat_col = columnas_posibles_lat[0]
    lon_col = columnas_posibles_lon[0]
    print(f"\n--- Rango geografico ---")
    print(f"  Latitud ({lat_col}): {df_full[lat_col].min():.4f} a {df_full[lat_col].max():.4f}")
    print(f"  Longitud ({lon_col}): {df_full[lon_col].min():.4f} a {df_full[lon_col].max():.4f}")