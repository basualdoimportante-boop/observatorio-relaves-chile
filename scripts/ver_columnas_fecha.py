# ============================================================
# VERIFICAR COLUMNAS DE FECHAS DISPONIBLES
# ============================================================

import pandas as pd
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

df = pd.read_csv(os.path.join(OUT_DIR, "ranking_con_precipitacion.csv"))

print("=" * 70)
print("COLUMNAS QUE CONTIENEN 'FECHA' O 'fecha'")
print("=" * 70)

columnas_fecha = [c for c in df.columns if "fecha" in c.lower()]
for col in columnas_fecha:
    print(f"  - {col}")
    print(f"    Valores no nulos: {df[col].notna().sum()}")
    print(f"    Ejemplo: {df[col].dropna().iloc[0] if df[col].notna().any() else 'vacio'}")

print("\n" + "=" * 70)
print("TODAS LAS COLUMNAS (primeras 50)")
print("=" * 70)

for i, col in enumerate(df.columns[:50], 1):
    print(f"  {i}. {col}")