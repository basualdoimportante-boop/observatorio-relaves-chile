# ============================================================
# DIAGNOSTICO CORREGIDO
# ============================================================

import geopandas as gpd
import pandas as pd
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

print("=" * 70)
print("DIAGNOSTICO CORREGIDO")
print("=" * 70)

# 1. CASERIOS
print("\n--- CASERIOS ---")
caserios = gpd.read_file(os.path.join(DATA_DIR, "caserios_2017", "Caserios_2017.shp"))
print(f"  Total: {len(caserios)}")
print(f"  CRS: {caserios.crs}")
print(f"  Tipos de geometria: {caserios.geometry.geom_type.unique()}")
print(f"  Columnas: {caserios.columns.tolist()}")

# Calcular centroides y verificar que caen en Chile
centroides = caserios.geometry.centroid
print(f"\n  Centroides (primeros 3):")
for i, geom in enumerate(centroides.head(3)):
    print(f"    {i}: X={geom.x:.4f}, Y={geom.y:.4f}")

# 2. DEPOSITOS
print("\n--- DEPOSITOS ---")
df = pd.read_csv(os.path.join(OUT_DIR, "ranking_final_1Mt.csv"))
print(f"  Total: {len(df)}")
print(f"  Rango LATITUD: {df['LATITUD'].min():.4f} a {df['LATITUD'].max():.4f}")
print(f"  Rango LONGITUD: {df['LONGITUD'].min():.4f} a {df['LONGITUD'].max():.4f}")

# 3. CREAR GEODATAFRAME EN WGS84
print("\n--- CREACION DE GEODATAFRAME ---")
depositos_wgs = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["LONGITUD"], df["LATITUD"]),
    crs="EPSG:4326"
)
print(f"  Depositos CRS: {depositos_wgs.crs}")

# 4. REPROYECTAR AMBOS A UTM 19S
print("\n--- REPROYECCION A UTM 19S ---")
caserios_utm = caserios.to_crs(epsg=32719)
depositos_utm = depositos_wgs.to_crs(epsg=32719)

print(f"  Caserios CRS: {caserios_utm.crs}")
print(f"  Depositos CRS: {depositos_utm.crs}")

# Verificar rangos UTM (deberian estar entre 200.000 y 700.000 en X)
print(f"\n  Depositos UTM (primeros 3):")
for i, geom in enumerate(depositos_utm.geometry.head(3)):
    print(f"    {i}: X={geom.x:.0f}, Y={geom.y:.0f}")

# Centroides de caserios
centroides_utm = caserios_utm.geometry.centroid
print(f"\n  Caserios UTM centroides (primeros 3):")
for i, geom in enumerate(centroides_utm.head(3)):
    print(f"    {i}: X={geom.x:.0f}, Y={geom.y:.0f}")

# 5. PRUEBA DE DISTANCIA MANUAL
print("\n--- PRUEBA DE DISTANCIA MANUAL ---")
dep0 = depositos_utm.iloc[0]
print(f"  Deposito: {dep0['cat_nombre_faena']}")
print(f"  Coordenadas UTM: X={dep0.geometry.x:.0f}, Y={dep0.geometry.y:.0f}")

# Distancia del deposito a TODOS los caserios
distancias = caserios_utm.geometry.distance(dep0.geometry)
print(f"  Distancia minima: {distancias.min():.0f} metros")
print(f"  Distancia maxima: {distancias.max():.0f} metros")
print(f"  Índice del más cercano: {distancias.idxmin()}")

# Info del caserio mas cercano
caserio_cercano = caserios_utm.loc[distancias.idxmin()]
print(f"\n  Caserio mas cercano:")
for col in caserios.columns:
    if col != "geometry":
        print(f"    {col}: {caserio_cercano[col]}")