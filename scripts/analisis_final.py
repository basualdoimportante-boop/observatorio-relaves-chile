# ============================================================
# ANALISIS FINAL - SOLO ELEMENTOS DE ALTA FIABILIDAD
# Censura < 10%. Rankings creibles.
# ============================================================

import pandas as pd
import numpy as np
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# ------------------------------------------------------------
# 1. ELEMENTOS DE ALTA FIABILIDAD (censura < 10%)
# ------------------------------------------------------------
ELEMENTOS_FIABLES = {
    # Metal base
    "CON_CU": {"nombre": "Cobre", "corteza": 28.0, "censura": 0.0},
    "CON_PB": {"nombre": "Plomo", "corteza": 17.0, "censura": 0.3},
    "CON_ZN": {"nombre": "Zinc", "corteza": 67.0, "censura": 7.9},
    
    # Elementos criticos fiables
    "CON_V": {"nombre": "Vanadio", "corteza": 107.0, "censura": 0.7},
    "CON_CR": {"nombre": "Cromo", "corteza": 92.0, "censura": 1.4},
    "CON_SC": {"nombre": "Escandio", "corteza": 14.0, "censura": 9.4},
    "CON_U": {"nombre": "Uranio", "corteza": 2.7, "censura": 0.3},
    "CON_TH": {"nombre": "Torio", "corteza": 10.5, "censura": 0.1},
    
    # Elementos traza fiables
    "CON_RB": {"nombre": "Rubidio", "corteza": 84.0, "censura": 1.0},
    "CON_SR": {"nombre": "Estroncio", "corteza": 320.0, "censura": 6.4},
    "CON_ZR": {"nombre": "Circonio", "corteza": 193.0, "censura": 0.6},
    "CON_CS": {"nombre": "Cesio", "corteza": 4.9, "censura": 0.1},
    "CON_HF": {"nombre": "Hafnio", "corteza": 5.3, "censura": 0.2},
    
    # Tierras raras (todas <1%)
    "CON_LA": {"nombre": "Lantano", "corteza": 20.0, "censura": 0.2},
    "CON_CE": {"nombre": "Cerio", "corteza": 43.0, "censura": 0.0},
    "CON_PR": {"nombre": "Praseodimio", "corteza": 5.1, "censura": 0.0},
    "CON_ND": {"nombre": "Neodimio", "corteza": 20.0, "censura": 0.0},
    "CON_SM": {"nombre": "Samario", "corteza": 3.9, "censura": 0.0},
    "CON_EU": {"nombre": "Europio", "corteza": 0.8, "censura": 0.0},
    "CON_GD": {"nombre": "Gadolinio", "corteza": 3.7, "censura": 0.0},
    "CON_TB": {"nombre": "Terbio", "corteza": 0.65, "censura": 0.0},
    "CON_DY": {"nombre": "Disprosio", "corteza": 3.5, "censura": 0.0},
    "CON_HO": {"nombre": "Holmio", "corteza": 0.8, "censura": 0.0},
    "CON_ER": {"nombre": "Erbio", "corteza": 2.3, "censura": 0.0},
    "CON_TM": {"nombre": "Tulio", "corteza": 0.33, "censura": 0.0},
    "CON_YB": {"nombre": "Iterbio", "corteza": 2.2, "censura": 0.0},
    "CON_LU": {"nombre": "Lutecio", "corteza": 0.32, "censura": 0.1},
}

TIERRAS_RARAS = [
    "CON_LA", "CON_CE", "CON_PR", "CON_ND", "CON_SM", "CON_EU",
    "CON_GD", "CON_TB", "CON_DY", "CON_HO", "CON_ER", "CON_TM",
    "CON_YB", "CON_LU",
]

# ------------------------------------------------------------
# 2. CARGAR
# ------------------------------------------------------------
print("=" * 75)
print("ANALISIS FINAL - ELEMENTOS DE ALTA FIABILIDAD")
print("=" * 75)

df = pd.read_csv(os.path.join(OUT_DIR, "maestro_relaves.csv"))
df = df.copy()
print(f"\nDepositos: {len(df)}")
print(f"Elementos analizados: {len(ELEMENTOS_FIABLES)}")

# ------------------------------------------------------------
# 3. CALCULAR EF CON MEDIANA
# ------------------------------------------------------------
print("\nCalculando factores de enriquecimiento...")

nuevas = {}
for elem, info in ELEMENTOS_FIABLES.items():
    col_med = f"{elem}_med"
    if col_med in df.columns:
        nombre_corto = elem.replace("CON_", "")
        nuevas[f"EF_{nombre_corto}"] = df[col_med] / info["corteza"]

df = pd.concat([df, pd.DataFrame(nuevas, index=df.index)], axis=1)

# ------------------------------------------------------------
# 4. RANKINGS POR ELEMENTO
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("TOP 10 DEPOSITOS POR ELEMENTO")
print("=" * 75)

for elem, info in ELEMENTOS_FIABLES.items():
    col_ef = f"EF_{elem.replace('CON_', '')}"
    if col_ef not in df.columns:
        continue
    
    top10 = df.dropna(subset=[col_ef]).nlargest(10, col_ef)
    print(f"\n--- {info['nombre']} ({elem}) ---")
    for i, (_, row) in enumerate(top10.iterrows(), 1):
        faena = str(row["cat_nombre_faena"])[:32]
        conf = row["confiabilidad"][:3]
        print(f"  {i:>2}. {faena:<34} EF={row[col_ef]:>7.2f} [{conf}]")

# ------------------------------------------------------------
# 5. RANKING DE TIERRAS RARAS
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("TOP 20 DEPOSITOS POR TIERRAS RARAS (EF promedio)")
print("=" * 75)

cols_ree = [f"EF_{e.replace('CON_', '')}" for e in TIERRAS_RARAS if f"EF_{e.replace('CON_', '')}" in df.columns]
df["EF_REE_avg"] = df[cols_ree].mean(axis=1)
df["EF_REE_max"] = df[cols_ree].max(axis=1)

top_ree = df.dropna(subset=["EF_REE_avg"]).nlargest(20, "EF_REE_avg")
for i, (_, row) in enumerate(top_ree.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:34]
    conf = row["confiabilidad"][:3]
    print(f"  {i:>2}. {faena:<36} EF_REE={row['EF_REE_avg']:>5.2f} (max {row['EF_REE_max']:.1f}) [{conf}]")

# ------------------------------------------------------------
# 6. DEPOSITOS MULTI-ELEMENTO (fiables)
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("DEPOSITOS CON MULTIPLES ELEMENTOS ENRIQUECIDOS")
print("=" * 75)

cols_ef = [f"EF_{e.replace('CON_', '')}" for e in ELEMENTOS_FIABLES if f"EF_{e.replace('CON_', '')}" in df.columns]

# Contar elementos con EF > 2 (excluyendo tierras raras para no duplicar)
cols_ef_sin_ree = [c for c in cols_ef if c not in cols_ree]

df["n_elementos_enriquecidos"] = (df[cols_ef_sin_ree] > 2).sum(axis=1)
df["n_ree_enriquecidas"] = (df[cols_ree] > 2).sum(axis=1)
df["n_total_enriquecidos"] = df["n_elementos_enriquecidos"] + df["n_ree_enriquecidas"]

print(f"\nDepositos con >= 3 elementos enriquecidos (EF>2): {(df['n_total_enriquecidos'] >= 3).sum()}")
print(f"Depositos con >= 5 elementos enriquecidos: {(df['n_total_enriquecidos'] >= 5).sum()}")
print(f"Depositos con >= 8 elementos enriquecidos: {(df['n_total_enriquecidos'] >= 8).sum()}")
print(f"Depositos con >= 10 elementos enriquecidos: {(df['n_total_enriquecidos'] >= 10).sum()}")

print("\nTop 20 depositos multi-elemento:")
top_multi = df.nlargest(20, "n_total_enriquecidos")[
    ["cat_id", "cat_nombre_faena", "cat_tonelaje_autorizado",
     "n_elementos_enriquecidos", "n_ree_enriquecidas", "n_total_enriquecidos", "confiabilidad"]
]
top_multi["tonelaje_Mt"] = top_multi["cat_tonelaje_autorizado"] / 1e6
print(top_multi[["cat_id", "cat_nombre_faena", "tonelaje_Mt", "n_elementos_enriquecidos", "n_ree_enriquecidas", "n_total_enriquecidos", "confiabilidad"]].to_string(index=False))

# ------------------------------------------------------------
# 7. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "maestro_analisis_final.csv")
df.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo guardado en: {ruta}")
print(f"  Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")

# Guardar solo los depositos con datos de tierras raras
ruta_ree = os.path.join(OUT_DIR, "top_tierras_raras.csv")
top_ree.to_csv(ruta_ree, index=False, encoding="utf-8")
print(f"Top tierras raras guardado en: {ruta_ree}")