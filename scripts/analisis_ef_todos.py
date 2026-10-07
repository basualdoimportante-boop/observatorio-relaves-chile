# ============================================================
# ANALISIS: FACTOR DE ENRIQUECIMIENTO PARA TODOS LOS ELEMENTOS
# Incluye elementos criticos y tierras raras
# ============================================================

import pandas as pd
import numpy as np
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# ------------------------------------------------------------
# CONCENTRACIONES DE REFERENCIA EN CORTEZA CONTINENTAL SUPERIOR (g/t)
# Fuente: Rudnick & Gao (2003), Taylor & McLennan (1985)
# ------------------------------------------------------------
CORTEZA = {
    # Metales base
    "CON_CU": 28.0,      # Cobre
    "CON_ZN": 67.0,      # Zinc
    "CON_PB": 17.0,      # Plomo
    "CON_NI": 47.0,      # Niquel
    "CON_CO": 17.3,      # Cobalto
    "CON_MO": 1.1,       # Molibdeno
    "CON_SN": 2.1,       # Estano
    
    # Metales preciosos
    "CON_AU": 0.0015,    # Oro (1.5 ppb)
    "CON_AG": 0.053,     # Plata
    
    # Elementos criticos
    "CON_V": 107.0,      # Vanadio
    "CON_CR": 92.0,      # Cromo
    "CON_W": 1.4,        # Wolframio
    "CON_TA": 0.9,       # Tantalio
    "CON_NB": 12.0,      # Niobio
    "CON_SB": 0.4,       # Antimonio
    "CON_BI": 0.16,      # Bismuto
    "CON_SC": 14.0,      # Escandio
    "CON_U": 2.7,        # Uranio
    "CON_TH": 10.5,      # Torio
    
    # Tierras raras (REEs)
    "CON_LA": 20.0,      # Lantano
    "CON_CE": 43.0,      # Cerio
    "CON_PR": 5.1,       # Praseodimio
    "CON_ND": 20.0,      # Neodimio
    "CON_SM": 3.9,       # Samario
    "CON_EU": 0.8,       # Europio
    "CON_GD": 3.7,       # Gadolinio
    "CON_TB": 0.65,      # Terbio
    "CON_DY": 3.5,       # Disprosio
    "CON_HO": 0.8,       # Holmio
    "CON_ER": 2.3,       # Erbio
    "CON_TM": 0.33,      # Tulio
    "CON_YB": 2.2,       # Iterbio
    "CON_LU": 0.32,      # Lutecio
    
    # Otros
    "CON_RB": 84.0,      # Rubidio
    "CON_SR": 320.0,     # Estroncio
    "CON_Y": 21.0,       # Itrio
    "CON_ZR": 193.0,     # Circonio
    "CON_BA": 628.0,     # Bario
    "CON_CS": 4.9,       # Cesio
    "CON_HF": 5.3,       # Hafnio
    "CON_AS": 4.8,       # Arsenico
    "CON_CD": 0.09,      # Cadmio
    "CON_HG": 0.05,      # Mercurio
}

# Elementos criticos (UE + EE.UU.)
ELEMENTOS_CRITICOS = [
    "CON_CO", "CON_NI", "CON_W", "CON_TA", "CON_NB", "CON_SB",
    "CON_BI", "CON_SC", "CON_U", "CON_TH", "CON_V", "CON_MO", "CON_SN",
]

# Tierras raras
TIERRAS_RARAS = [
    "CON_LA", "CON_CE", "CON_PR", "CON_ND", "CON_SM", "CON_EU",
    "CON_GD", "CON_TB", "CON_DY", "CON_HO", "CON_ER", "CON_TM",
    "CON_YB", "CON_LU",
]


# ------------------------------------------------------------
# 1. CARGAR ARCHIVO MAESTRO
# ------------------------------------------------------------
print("=" * 70)
print("ANALISIS DE ENRIQUECIMIENTO PARA TODOS LOS ELEMENTOS")
print("=" * 70)

df = pd.read_csv(os.path.join(OUT_DIR, "maestro_relaves.csv"))
df = df.copy()  # Desfragmentar
print(f"\nDepositos: {len(df)}")

# ------------------------------------------------------------
# 2. CALCULAR EF PARA CADA ELEMENTO (usando promedio)
# ------------------------------------------------------------
print("\nCalculando factores de enriquecimiento...")

nuevas_columnas = {}
for elem, corteza in CORTEZA.items():
    col_prom = f"{elem}_prom"
    if col_prom in df.columns:
        nuevas_columnas[f"EF_{elem.replace('CON_', '')}"] = df[col_prom] / corteza

# Agregar todas las columnas de una vez (evita PerformanceWarning)
df_ef = pd.concat([df, pd.DataFrame(nuevas_columnas, index=df.index)], axis=1)
print(f"  Elementos calculados: {len(nuevas_columnas)}")

# ------------------------------------------------------------
# 3. RANKING DE CADA ELEMENTO CRITICO
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("TOP 5 DEPOSITOS POR CADA ELEMENTO CRITICO")
print("=" * 70)

for elem in ELEMENTOS_CRITICOS:
    col_ef = f"EF_{elem.replace('CON_', '')}"
    if col_ef not in df_ef.columns:
        continue
    
    top5 = df_ef.dropna(subset=[col_ef]).nlargest(5, col_ef)
    nombre = elem.replace("CON_", "")
    print(f"\n--- {nombre} ---")
    for i, (_, row) in enumerate(top5.iterrows(), 1):
        faena = str(row["cat_nombre_faena"])[:30]
        print(f"  {i}. {faena:<32} EF={row[col_ef]:.1f}")

# ------------------------------------------------------------
# 4. RANKING COMBINADO DE TIERRAS RARAS
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("TOP 10 DEPOSITOS POR TIERRAS RARAS (EF promedio)")
print("=" * 70)

columnas_ree = [f"EF_{e.replace('CON_', '')}" for e in TIERRAS_RARAS]
columnas_ree = [c for c in columnas_ree if c in df_ef.columns]

df_ef["EF_REE_avg"] = df_ef[columnas_ree].mean(axis=1)
top_ree = df_ef.dropna(subset=["EF_REE_avg"]).nlargest(10, "EF_REE_avg")

for i, (_, row) in enumerate(top_ree.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:35]
    print(f"  {i}. {faena:<37} EF_REE={row['EF_REE_avg']:.2f}")

# ------------------------------------------------------------
# 5. DEPOSITOS MULTI-ELEMENTO
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("DEPOSITOS CON MULTIPLES ELEMENTOS ENRIQUECIDOS (EF > 2)")
print("=" * 70)

# Contar cuantos elementos criticos tienen EF > 2
columnas_ef_criticos = [f"EF_{e.replace('CON_', '')}" for e in ELEMENTOS_CRITICOS]
columnas_ef_criticos = [c for c in columnas_ef_criticos if c in df_ef.columns]

df_ef["n_criticos_enriquecidos"] = (df_ef[columnas_ef_criticos] > 2).sum(axis=1)
df_ef["n_ree_enriquecidos"] = (df_ef[columnas_ree] > 2).sum(axis=1)

print(f"\nDepositos con >= 1 critico enriquecido (EF>2): {(df_ef['n_criticos_enriquecidos'] >= 1).sum()}")
print(f"Depositos con >= 3 criticos enriquecidos: {(df_ef['n_criticos_enriquecidos'] >= 3).sum()}")
print(f"Depositos con >= 5 criticos enriquecidos: {(df_ef['n_criticos_enriquecidos'] >= 5).sum()}")

print(f"\nDepositos con >= 3 REE enriquecidas: {(df_ef['n_ree_enriquecidos'] >= 3).sum()}")
print(f"Depositos con >= 5 REE enriquecidas: {(df_ef['n_ree_enriquecidos'] >= 5).sum()}")

# Top 10 multi-elemento
print("\nTop 10 depositos multi-elemento:")
top_multi = df_ef.nlargest(10, "n_criticos_enriquecidos")[
    ["cat_id", "cat_nombre_faena", "n_criticos_enriquecidos", "n_ree_enriquecidos", "confiabilidad"]
]
print(top_multi.to_string(index=False))

# ------------------------------------------------------------
# 6. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "maestro_con_ef_completo.csv")
df_ef.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo completo guardado en: {ruta}")
print(f"  Dimensiones: {df_ef.shape[0]} filas x {df_ef.shape[1]} columnas")