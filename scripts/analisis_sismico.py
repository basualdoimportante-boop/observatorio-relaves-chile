# ============================================================
# ANALISIS DE AMENAZA SISMICA (v2 - con fechas recuperadas)
# ============================================================

import pandas as pd
import numpy as np
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

print("=" * 75)
print("ANALISIS DE AMENAZA SISMICA")
print("=" * 75)

# ------------------------------------------------------------
# 1. CARGAR DATOS
# ------------------------------------------------------------
print("\n[1] Cargando datos...")

amenaza = pd.read_csv(os.path.join(DATA_DIR, "mapa_amenaza.csv"))
print(f"  Puntos de amenaza: {len(amenaza):,}")

# Usar el archivo CON FECHAS
df = pd.read_csv(os.path.join(OUT_DIR, "ranking_con_fechas.csv"))
df = df.copy()
print(f"  Depositos: {len(df)}")

# ------------------------------------------------------------
# 2. ASIGNAR AMENAZA SISMICA
# ------------------------------------------------------------
print("\n[2] Asignando amenaza sismica (vecino mas cercano)...")

dep_lat = df["LATITUD"].values
dep_lon = df["LONGITUD"].values
grid_lat = amenaza["lat"].values
grid_lon = amenaza["lon"].values

# Metricas: SA(0.3)-0.02 es el mejor predictor para relaves
col_sa03 = "SA(0.3)-0.02"
col_pga = "PGA-0.1"
grid_sa03 = amenaza[col_sa03].values
grid_pga = amenaza[col_pga].values

sa03_result = []
pga_result = []

for i in range(len(df)):
    dist = np.sqrt((grid_lat - dep_lat[i])**2 + (grid_lon - dep_lon[i])**2)
    idx_min = np.argmin(dist)
    sa03_result.append(grid_sa03[idx_min])
    pga_result.append(grid_pga[idx_min])

df["SA_0_3_02"] = sa03_result
df["PGA_0_1"] = pga_result

print(f"  Completado")

# ------------------------------------------------------------
# 3. CLASIFICAR AMENAZA SISMICA
# ------------------------------------------------------------
print("\n[3] Clasificando amenaza sismica...")

def clasificar_sa03(valor):
    if pd.isna(valor):
        return "DESCONOCIDA"
    elif valor >= 1.0:
        return "MUY_ALTA"
    elif valor >= 0.7:
        return "ALTA"
    elif valor >= 0.4:
        return "MEDIA"
    elif valor >= 0.2:
        return "BAJA"
    else:
        return "MUY_BAJA"

df["nivel_amenaza_sismica"] = df["SA_0_3_02"].apply(clasificar_sa03)

# ------------------------------------------------------------
# 4. ALERTAS SISMICAS
# ------------------------------------------------------------
print("\n[4] Generando alertas sismicas...")

df["ALERTA_SISMICA_MUY_ALTA"] = df["SA_0_3_02"] >= 1.0
df["ALERTA_SISMICA_ALTA"] = (df["SA_0_3_02"] >= 0.7) & (df["SA_0_3_02"] < 1.0)

# Antiguedad (solo si tiene fecha)
df["ALERTA_ANTIGUEDAD"] = df["antiguedad_anios"] >= 30

# Alerta critica: amenaza alta + antiguedad
df["ALERTA_SISMICA_CRITICA"] = (
    (df["SA_0_3_02"] >= 0.7) &
    (df["antiguedad_anios"] >= 30)
)

# Actualizar contador de alertas
columnas_alerta = [c for c in df.columns if c.startswith("ALERTA_")]
df["n_alertas"] = df[columnas_alerta].sum(axis=1)

def listar_alertas(row):
    activas = [c.replace("ALERTA_", "") for c in columnas_alerta if row[c]]
    return ", ".join(activas) if activas else "NINGUNA"

df["alertas_activas"] = df.apply(listar_alertas, axis=1)

# ------------------------------------------------------------
# 5. REPORTE
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("RESULTADOS DE AMENAZA SISMICA")
print("=" * 75)

print("\nDistribucion por nivel de amenaza:")
for nivel in ["MUY_ALTA", "ALTA", "MEDIA", "BAJA", "MUY_BAJA"]:
    cant = (df["nivel_amenaza_sismica"] == nivel).sum()
    pct = 100 * cant / len(df)
    print(f"  {nivel:<12}: {cant:>3} ({pct:.1f}%)")

print(f"\nDepositos con amenaza MUY ALTA (SA>1g): {df['ALERTA_SISMICA_MUY_ALTA'].sum()}")
print(f"Depositos con amenaza ALTA (SA>0.7g): {df['ALERTA_SISMICA_ALTA'].sum()}")
print(f"Depositos antiguos (>30 anios): {df['ALERTA_ANTIGUEDAD'].sum()}")
print(f"Depositos con ALERTA SISMICA CRITICA: {df['ALERTA_SISMICA_CRITICA'].sum()}")

# Top 20 con mayor amenaza
print("\n" + "=" * 75)
print("TOP 20 DEPOSITOS CON MAYOR AMENAZA SISMICA")
print("=" * 75)

top = df.nlargest(20, "SA_0_3_02")[
    ["cat_id", "cat_nombre_faena", "cat_tonelaje_autorizado",
     "SA_0_3_02", "PGA_0_1", "anio_aprobacion", "antiguedad_anios",
     "nivel_amenaza_sismica", "indice_riesgo"]
].copy()
top["tonelaje_Mt"] = (top["cat_tonelaje_autorizado"] / 1e6).round(1)

print(f"\n{'#':<3} {'ID':<11} {'Faena':<28} {'Mt':>7} {'SA0.3':>7} {'Anio':>6} {'Antig':>6} {'Índ':>4}")
print("-" * 95)
for i, (_, row) in enumerate(top.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:26]
    anio = int(row["anio_aprobacion"]) if pd.notna(row["anio_aprobacion"]) else 0
    antig = int(row["antiguedad_anios"]) if pd.notna(row["antiguedad_anios"]) else 0
    print(f"{i:<3} {row['cat_id']:<11} {faena:<28} {row['tonelaje_Mt']:>7.1f} {row['SA_0_3_02']:>7.2f} {anio:>6} {antig:>6} {row['indice_riesgo']:>4}")

# Casos con alerta critica
print("\n" + "=" * 75)
print("DEPOSITOS CON ALERTA SISMICA CRITICA (amenaza + antiguedad)")
print("=" * 75)

criticos = df[df["ALERTA_SISMICA_CRITICA"]].sort_values("SA_0_3_02", ascending=False)
print(f"\nTotal: {len(criticos)}")
for _, row in criticos.iterrows():
    faena = str(row["cat_nombre_faena"])[:33]
    mt = row["cat_tonelaje_autorizado"] / 1e6
    anio = int(row["anio_aprobacion"]) if pd.notna(row["anio_aprobacion"]) else 0
    print(f"  {row['cat_id']:<11} {faena:<35} {mt:>7.1f} Mt | SA={row['SA_0_3_02']:.2f}g | {anio} | Índ={row['indice_riesgo']}")

# ------------------------------------------------------------
# 6. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "ranking_final_completo.csv")
df.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo guardado en: {ruta}")
print(f"  Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")

print(f"\n--- Distribucion final de alertas ---")
for col in columnas_alerta:
    cant = df[col].sum()
    nombre = col.replace("ALERTA_", "")
    print(f"  {nombre:<30}: {cant:>3}")