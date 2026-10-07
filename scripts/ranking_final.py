# ============================================================
# RANKING FINAL CON FILTRO DE TONELAJE (>= 1 Mt)
# ============================================================

import pandas as pd
import numpy as np
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# ------------------------------------------------------------
# 1. CARGAR
# ------------------------------------------------------------
print("=" * 75)
print("RANKING FINAL - DEPOSITOS CON >= 1 MILLON DE TONELADAS")
print("=" * 75)

df = pd.read_csv(os.path.join(OUT_DIR, "maestro_analisis_final.csv"))
print(f"\nDepositos totales: {len(df)}")

# ------------------------------------------------------------
# 2. APLICAR FILTRO DE TONELAJE
# ------------------------------------------------------------
# Usar tonelaje autorizado, con tonelaje actual como respaldo
df["tonelaje_ref"] = df["cat_tonelaje_autorizado"].fillna(df.get("TONELAJE_ACTUAL", np.nan))

# Filtrar
df_filtrado = df[df["tonelaje_ref"] >= 1_000_000].copy()
print(f"Depositos con >= 1 Mt: {len(df_filtrado)}")
print(f"Tonelaje total filtrado: {df_filtrado['tonelaje_ref'].sum()/1e9:.2f} mil millones de toneladas")

# ------------------------------------------------------------
# 3. RANKING MULTI-ELEMENTO (solo elementos fiables)
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("TOP 25 DEPOSITOS MULTI-ELEMENTO (>= 1 Mt)")
print("=" * 75)

cols_ef = [c for c in df_filtrado.columns if c.startswith("EF_") and c != "EF_REE_avg" and c != "EF_REE_max"]
cols_ree = [c for c in cols_ef if any(ree in c for ree in [
    "EF_LA", "EF_CE", "EF_PR", "EF_ND", "EF_SM", "EF_EU", "EF_GD",
    "EF_TB", "EF_DY", "EF_HO", "EF_ER", "EF_TM", "EF_YB", "EF_LU"
])]
cols_sin_ree = [c for c in cols_ef if c not in cols_ree]

df_filtrado["n_enriquecidos"] = (df_filtrado[cols_ef] > 2).sum(axis=1)
df_filtrado["n_ree"] = (df_filtrado[cols_ree] > 2).sum(axis=1)

top = df_filtrado.nlargest(25, "n_enriquecidos")[
    ["cat_id", "cat_nombre_faena", "tonelaje_ref", "n_enriquecidos", "n_ree",
     "cat_estado", "cat_nombre_instalacion", "confiabilidad"]
].copy()
top["tonelaje_Mt"] = (top["tonelaje_ref"] / 1e6).round(1)

print(f"\n{'#':<4} {'ID':<12} {'Faena':<38} {'Mt':>8} {'Elem':>5} {'REE':>4} {'Estado':<12}")
print("-" * 100)
for i, (_, row) in enumerate(top.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:36]
    estado = str(row["cat_estado"])[:10]
    print(f"{i:<4} {row['cat_id']:<12} {faena:<38} {row['tonelaje_Mt']:>8.1f} {row['n_enriquecidos']:>5} {row['n_ree']:>4} {estado:<12}")

# ------------------------------------------------------------
# 4. TOP 15 TIERRAS RARAS (>= 1 Mt)
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("TOP 15 TIERRAS RARAS (>= 1 Mt)")
print("=" * 75)

top_ree = df_filtrado.dropna(subset=["EF_REE_avg"]).nlargest(15, "EF_REE_avg")[
    ["cat_id", "cat_nombre_faena", "tonelaje_ref", "EF_REE_avg", "EF_REE_max", "confiabilidad"]
].copy()
top_ree["tonelaje_Mt"] = (top_ree["tonelaje_ref"] / 1e6).round(1)

print(f"\n{'#':<4} {'ID':<12} {'Faena':<38} {'Mt':>8} {'EF_REE':>8} {'Max':>6}")
print("-" * 85)
for i, (_, row) in enumerate(top_ree.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:36]
    print(f"{i:<4} {row['cat_id']:<12} {faena:<38} {row['tonelaje_Mt']:>8.1f} {row['EF_REE_avg']:>8.2f} {row['EF_REE_max']:>6.1f}")

# ------------------------------------------------------------
# 5. TOP 5 POR ELEMENTO INDIVIDUAL (>= 1 Mt)
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("TOP 5 POR ELEMENTO INDIVIDUAL (>= 1 Mt)")
print("=" * 75)

elementos_mostrar = ["EF_CU", "EF_ZN", "EF_PB", "EF_V", "EF_CS", "EF_RB", "EF_SC", "EF_U"]

for col in elementos_mostrar:
    if col not in df_filtrado.columns:
        continue
    nombre = col.replace("EF_", "")
    top5 = df_filtrado.dropna(subset=[col]).nlargest(5, col)
    print(f"\n--- {nombre} ---")
    for i, (_, row) in enumerate(top5.iterrows(), 1):
        faena = str(row["cat_nombre_faena"])[:36]
        mt = row["tonelaje_ref"] / 1e6
        print(f"  {i}. {faena:<38} EF={row[col]:>7.2f} ({mt:.1f} Mt)")

# ------------------------------------------------------------
# 6. RESUMEN POR REGION
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("DISTRIBUCION POR REGION (>= 1 Mt)")
print("=" * 75)

por_region = df_filtrado.groupby("REGION").agg(
    n_depositos=("cat_id", "count"),
    tonelaje_total_Mt=("tonelaje_ref", lambda x: x.sum()/1e6),
    ef_ree_promedio=("EF_REE_avg", "mean"),
).sort_values("tonelaje_total_Mt", ascending=False)

print(por_region.to_string())

# ------------------------------------------------------------
# 7. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "ranking_final_1Mt.csv")
df_filtrado.to_csv(ruta, index=False, encoding="utf-8")
print(f"\n\nArchivo guardado en: {ruta}")
print(f"Depositos filtrados: {len(df_filtrado)}")