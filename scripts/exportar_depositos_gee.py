# ============================================================
# EXPORTAR DEPOSITOS PARA GOOGLE EARTH ENGINE
# Genera un CSV con las coordenadas de los 109 depositos
# ============================================================

import pandas as pd
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

print("=" * 70)
print("EXPORTANDO DEPOSITOS PARA GEE")
print("=" * 70)

# Cargar el ranking con alertas
df = pd.read_csv(os.path.join(OUT_DIR, "ranking_con_alertas.csv"))
print(f"\nDepositos: {len(df)}")

# Seleccionar columnas necesarias para GEE
# GEE necesita: ID, latitud, longitud
df_gee = df[["cat_id", "cat_nombre_faena", "LATITUD", "LONGITUD"]].copy()

# Verificar que no haya valores nulos en coordenadas
nulos = df_gee[["LATITUD", "LONGITUD"]].isna().sum()
print(f"\nValores nulos en LATITUD: {nulos['LATITUD']}")
print(f"Valores nulos en LONGITUD: {nulos['LONGITUD']}")

# Renombrar columnas para GEE (nombres simples sin caracteres especiales)
df_gee.columns = ["id", "nombre", "lat", "lon"]

# Verificar rangos
print(f"\nRango lat: {df_gee['lat'].min():.4f} a {df_gee['lat'].max():.4f}")
print(f"Rango lon: {df_gee['lon'].min():.4f} a {df_gee['lon'].max():.4f}")

# Guardar
ruta = os.path.join(OUT_DIR, "depositos_para_gee.csv")
df_gee.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo guardado en: {ruta}")

# Mostrar las primeras 5 filas
print(f"\nPrimeras 5 filas:")
print(df_gee.head().to_string(index=False))