# ============================================================
# ANALISIS: FACTOR DE ENRIQUECIMIENTO (EF) DE COBALTO
# Validacion contra la Tabla S4 del articulo Minerals 2026
# ============================================================

import pandas as pd
import numpy as np
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# ------------------------------------------------------------
# 1. CARGAR ARCHIVO MAESTRO
# ------------------------------------------------------------
print("=" * 70)
print("ANALISIS DE FACTOR DE ENRIQUECIMIENTO (EF) DE COBALTO")
print("=" * 70)

df = pd.read_csv(os.path.join(OUT_DIR, "maestro_relaves.csv"))
print(f"\nDepositos en el archivo: {len(df)}")

# ------------------------------------------------------------
# 2. CALCULAR FACTOR DE ENRIQUECIMIENTO
# ------------------------------------------------------------
CO_CORTEZA = 17.3  # g/t (concentracion en corteza continental superior)

# Calcular EF usando el promedio, la mediana y el maximo
df["EF_Co_prom"] = df["CON_CO_prom"] / CO_CORTEZA
df["EF_Co_med"] = df["CON_CO_med"] / CO_CORTEZA
df["EF_Co_max"] = df["CON_CO_max"] / CO_CORTEZA

print(f"\nCorteza continental (referencia): {CO_CORTEZA} g/t")
print(f"Depositos con dato de Co: {df['CON_CO_prom'].notna().sum()}")

# ------------------------------------------------------------
# 3. TOP 40 POR EF (usando promedio)
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("TOP 40 DEPOSITOS POR FACTOR DE ENRIQUECIMIENTO (promedio)")
print("=" * 70)

top40 = df.dropna(subset=["EF_Co_prom"]).nlargest(40, "EF_Co_prom")

print(f"\n{'#':<4} {'cat_id':<12} {'Faena':<35} {'Co_prom':<10} {'EF':<8}")
print("-" * 75)

for i, (idx, row) in enumerate(top40.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:33]
    print(f"{i:<4} {row['cat_id']:<12} {faena:<35} {row['CON_CO_prom']:<10.1f} {row['EF_Co_prom']:<8.1f}")

# ------------------------------------------------------------
# 4. ESTADISTICAS GENERALES
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("ESTADISTICAS DE ENRIQUECIMIENTO")
print("=" * 70)

con_co = df["CON_CO_prom"].dropna()
print(f"\nDepositos con dato de Co: {len(con_co)}")
print(f"  Mediana de Co: {con_co.median():.1f} g/t")
print(f"  Media de Co: {con_co.mean():.1f} g/t")
print(f"  Maximo de Co: {con_co.max():.1f} g/t")

# Cuantos depositos estan enriquecidos (EF > 1)
enriquecidos = (df["EF_Co_prom"] > 1).sum()
enriquecidos_2x = (df["EF_Co_prom"] > 2).sum()
enriquecidos_5x = (df["EF_Co_prom"] > 5).sum()

print(f"\nDepositos con EF > 1 (enriquecidos): {enriquecidos} ({100*enriquecidos/len(df):.1f}%)")
print(f"Depositos con EF > 2: {enriquecidos_2x} ({100*enriquecidos_2x/len(df):.1f}%)")
print(f"Depositos con EF > 5: {enriquecidos_5x} ({100*enriquecidos_5x/len(df):.1f}%)")

# ------------------------------------------------------------
# 5. GUARDAR RESULTADOS
# ------------------------------------------------------------
# Guardar el archivo maestro con las nuevas columnas
ruta = os.path.join(OUT_DIR, "maestro_con_ef.csv")
df.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo con EF guardado en: {ruta}")

# Guardar el top 40 en CSV aparte
ruta_top40 = os.path.join(OUT_DIR, "top40_ef_cobalto.csv")
top40.to_csv(ruta_top40, index=False, encoding="utf-8")
print(f"Top 40 guardado en: {ruta_top40}")