# ============================================================
# RECUPERAR FECHAS DEL CATASTRO ORIGINAL
# ============================================================

import pandas as pd
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

print("=" * 75)
print("RECUPERANDO FECHAS DEL CATASTRO")
print("=" * 75)

# 1. Cargar el ranking actual
df = pd.read_csv(os.path.join(OUT_DIR, "ranking_con_precipitacion.csv"))
print(f"\nRanking actual: {len(df)} depositos")
print(f"Columnas actuales: {len(df.columns)}")

# 2. Cargar el catastro original (que tiene las fechas)
cat = pd.read_csv(os.path.join(DATA_DIR, "live_catastro.csv"))
print(f"\nCatastro original: {len(cat)} depositos")

# Ver que columnas de fecha tiene el catastro
cols_fecha = [c for c in cat.columns if "FECHA" in c.upper()]
print(f"Columnas de fecha en catastro: {cols_fecha}")

# 3. Hacer merge para recuperar las fechas
# Usar cat_id del ranking y ID del catastro
cat_subset = cat[["ID", "FECHA_RES_APRUEBA", "FECHA_RES_PDC"]].copy()
cat_subset = cat_subset.rename(columns={"ID": "cat_id"})

df = df.merge(cat_subset, on="cat_id", how="left")

print(f"\nFechas recuperadas:")
print(f"  Con FECHA_RES_APRUEBA: {df['FECHA_RES_APRUEBA'].notna().sum()}")
print(f"  Con FECHA_RES_PDC: {df['FECHA_RES_PDC'].notna().sum()}")

# 4. Ahora si, calcular antiguedad
print("\n" + "=" * 75)
print("CALCULANDO ANTIGUEDAD")
print("=" * 75)

df["FECHA_RES_APRUEBA_DT"] = pd.to_datetime(df["FECHA_RES_APRUEBA"], errors="coerce")
anio_actual = 2026
df["anio_aprobacion"] = df["FECHA_RES_APRUEBA_DT"].dt.year
df["antiguedad_anios"] = anio_actual - df["anio_aprobacion"]

print(f"  Depositos con fecha valida: {df['FECHA_RES_APRUEBA_DT'].notna().sum()}")
print(f"  Anio mas antiguo: {df['anio_aprobacion'].min():.0f}")
print(f"  Anio mas reciente: {df['anio_aprobacion'].max():.0f}")
print(f"  Antiguedad mediana: {df['antiguedad_anios'].median():.0f} anios")
print(f"  Antiguedad maxima: {df['antiguedad_anios'].max():.0f} anios")

# Distribucion de antiguedad
print("\nDistribucion por rango de antiguedad:")
rangos = [
    (0, 10, "0-10 anios (reciente)"),
    (10, 20, "10-20 anios"),
    (20, 30, "20-30 anios"),
    (30, 50, "30-50 anios (antiguo)"),
    (50, 200, ">50 anios (muy antiguo)"),
]
for min_a, max_a, nombre in rangos:
    cant = ((df["antiguedad_anios"] >= min_a) & (df["antiguedad_anios"] < max_a)).sum()
    pct = 100 * cant / len(df)
    print(f"  {nombre:<28}: {cant:>3} ({pct:.1f}%)")

# 5. Guardar el ranking actualizado
ruta = os.path.join(OUT_DIR, "ranking_con_fechas.csv")
df.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo guardado en: {ruta}")
print(f"  Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
