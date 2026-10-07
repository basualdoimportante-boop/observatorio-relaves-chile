# ============================================================
# DIAGNOSTICO: COMO CRUZAR LOS TRES ARCHIVOS
# ============================================================

import pandas as pd
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"

# Cargar los tres archivos
geoq = pd.read_csv(os.path.join(DATA_DIR, "live_geoquimica.csv"))
otras = pd.read_csv(os.path.join(DATA_DIR, "live_otras_mediciones.csv"))
cat = pd.read_csv(os.path.join(DATA_DIR, "live_catastro.csv"))

print("=" * 70)
print("DIAGNOSTICO DE COLUMNAS PARA CRUCE")
print("=" * 70)

print("\n--- GEOQUIMICA: columnas completas ---")
for i, col in enumerate(geoq.columns, 1):
    print(f"  {i}. {col}")

print("\n--- CATASTRO: columnas completas ---")
for i, col in enumerate(cat.columns, 1):
    print(f"  {i}. {col}")

print("\n--- OTRAS MEDICIONES: columnas completas ---")
for i, col in enumerate(otras.columns, 1):
    print(f"  {i}. {col}")

# Buscar columnas comunes
print("\n" + "=" * 70)
print("COLUMNAS COMUNES ENTRE GEOQUIMICA Y CATASTRO")
print("=" * 70)
comunes_geoq_cat = set(geoq.columns) & set(cat.columns)
for col in sorted(comunes_geoq_cat):
    print(f"  - {col}")

print("\n" + "=" * 70)
print("COLUMNAS COMUNES ENTRE OTRAS_MEDICIONES Y CATASTRO")
print("=" * 70)
comunes_otras_cat = set(otras.columns) & set(cat.columns)
for col in sorted(comunes_otras_cat):
    print(f"  - {col}")

# Verificar si hay coincidencia en NOMBRE_FAE y NOMBRE_INSTALACION
print("\n" + "=" * 70)
print("PRUEBA DE CRUCE POR NOMBRES")
print("=" * 70)

# En geoquimica: NOMBRE_FAE y NOMBRE_INS
# En catastro: NOMBRE_FAENA y NOMBRE_INSTALACION

if "NOMBRE_FAE" in geoq.columns and "NOMBRE_FAENA" in cat.columns:
    faenas_geoq = set(geoq["NOMBRE_FAE"].dropna().str.upper().str.strip())
    faenas_cat = set(cat["NOMBRE_FAENA"].dropna().str.upper().str.strip())
    coincidencias = faenas_geoq & faenas_cat
    print(f"\nNombre de faena - geoquimica: {len(faenas_geoq)} valores unicos")
    print(f"Nombre de faena - catastro: {len(faenas_cat)} valores unicos")
    print(f"Coincidencias exactas: {len(coincidencias)}")
    print(f"\nEjemplos de coincidencias: {sorted(list(coincidencias))[:10]}")
    