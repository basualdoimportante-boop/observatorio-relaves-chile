# ============================================================
# ANALISIS DE CERCANIA A CENTROS POBLADOS (version corregida)
# Usa metodo manual de distancia (verificado)
# ============================================================

import geopandas as gpd
import pandas as pd
import numpy as np
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# ------------------------------------------------------------
# 1. CARGAR DATOS
# ------------------------------------------------------------
print("=" * 70)
print("ANALISIS DE CERCANIA A CENTROS POBLADOS")
print("=" * 70)

print("\nCargando datos...")
caserios = gpd.read_file(os.path.join(DATA_DIR, "caserios_2017", "Caserios_2017.shp"))
df = pd.read_csv(os.path.join(OUT_DIR, "ranking_final_1Mt.csv"))

print(f"  Caserios: {len(caserios)}")
print(f"  Depositos: {len(df)}")

# ------------------------------------------------------------
# 2. REPROYECTAR TODO A UTM 19S
# ------------------------------------------------------------
caserios_utm = caserios.to_crs(epsg=32719)

depositos_wgs = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["LONGITUD"], df["LATITUD"]),
    crs="EPSG:4326"
)
depositos_utm = depositos_wgs.to_crs(epsg=32719)

# Usar centroides de caserios (son poligonos)
caserios_centroides = caserios_utm.geometry.centroid

print("\nDatos reproyectados a UTM 19S")

# ------------------------------------------------------------
# 3. CALCULAR DISTANCIA AL CASERIO MAS CERCANO
# ------------------------------------------------------------
print("\nCalculando distancias (puede tardar 30-60 segundos)...")

resultados = []

for i, (idx, deposito) in enumerate(depositos_utm.iterrows(), 1):
    if i % 20 == 0:
        print(f"  Procesados {i}/{len(depositos_utm)}...")
    
    # Distancia del deposito a TODOS los caserios
    distancias = caserios_centroides.distance(deposito.geometry)
    
    # Indice del mas cercano
    idx_min = distancias.idxmin()
    distancia_min = distancias.loc[idx_min]
    
    # Info del caserio mas cercano
    caserio = caserios.loc[idx_min]
    
    resultados.append({
        "cat_id": deposito["cat_id"],
        "distancia_caserio_m": distancia_min,
        "caserio_nombre": caserio["NOM_LOC"],
        "caserio_categoria": caserio["CATEGORIA"],
        "caserio_poblacion": caserio["TOT_PERSON"],
        "caserio_comuna": caserio["NOM_COMUNA"],
        "caserio_region": caserio["NOM_REGION"],
    })

df_resultados = pd.DataFrame(resultados)

# ------------------------------------------------------------
# 4. UNIR CON EL DATAFRAME ORIGINAL
# ------------------------------------------------------------
df = df.merge(df_resultados, on="cat_id", how="left")

# ------------------------------------------------------------
# 5. CLASIFICAR POR NIVEL DE EXPOSICION
# ------------------------------------------------------------
def clasificar_exposicion(dist_m):
    if pd.isna(dist_m):
        return "DESCONOCIDA"
    elif dist_m < 500:
        return "MUY_ALTA"
    elif dist_m < 2000:
        return "ALTA"
    elif dist_m < 5000:
        return "MEDIA"
    elif dist_m < 10000:
        return "BAJA"
    else:
        return "MUY_BAJA"

df["exposicion_poblados"] = df["distancia_caserio_m"].apply(clasificar_exposicion)

# ------------------------------------------------------------
# 6. REPORTE
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("RESULTADOS DE CERCANIA A POBLADOS")
print("=" * 70)

print("\nDistribucion por nivel de exposicion:")
for nivel in ["MUY_ALTA", "ALTA", "MEDIA", "BAJA", "MUY_BAJA"]:
    cant = (df["exposicion_poblados"] == nivel).sum()
    pct = 100 * cant / len(df)
    print(f"  {nivel:<15}: {cant:>3} ({pct:.1f}%)")

print("\nEstadisticas de distancia (metros):")
dist = df["distancia_caserio_m"].dropna()
print(f"  Minima: {dist.min():.0f}")
print(f"  Mediana: {dist.median():.0f}")
print(f"  Media: {dist.mean():.0f}")
print(f"  Maxima: {dist.max():.0f}")

# Top 20 mas cercanos
print("\n" + "=" * 70)
print("TOP 20 DEPOSITOS MAS CERCANOS A POBLADOS")
print("=" * 70)

top_cerca = df.nsmallest(20, "distancia_caserio_m")[
    ["cat_id", "cat_nombre_faena", "cat_tonelaje_autorizado",
     "distancia_caserio_m", "caserio_nombre", "caserio_poblacion",
     "exposicion_poblados", "REGION"]
].copy()
top_cerca["tonelaje_Mt"] = (top_cerca["cat_tonelaje_autorizado"] / 1e6).round(1)

print(f"\n{'#':<4} {'ID':<12} {'Faena':<30} {'Mt':>7} {'Dist(m)':>9} {'Caserio':<25} {'Pob':>6}")
print("-" * 100)
for i, (_, row) in enumerate(top_cerca.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:28]
    caserio = str(row["caserio_nombre"])[:23]
    pob = int(row["caserio_poblacion"]) if pd.notna(row["caserio_poblacion"]) else 0
    print(f"{i:<4} {row['cat_id']:<12} {faena:<30} {row['tonelaje_Mt']:>7.1f} {row['distancia_caserio_m']:>9.0f} {caserio:<25} {pob:>6}")

# ------------------------------------------------------------
# 7. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "ranking_con_exposicion.csv")
df.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo guardado en: {ruta}")