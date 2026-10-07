# ============================================================
# ANALISIS DE ENRIQUECIMIENTO - SOLO ELEMENTOS FIABLES
# Separa elementos por tasa de censura (datos bajo limite de deteccion)
# ============================================================

import pandas as pd
import numpy as np
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# ------------------------------------------------------------
# TASAS DE CENSURA (% de muestras bajo el limite de deteccion)
# Fuente: Tabla S1 del articulo Minerals 2026
# ------------------------------------------------------------
CENSURA = {
    "CON_CU": 0.0,     # Cobre - sin censura
    "CON_PB": 0.3,     # Plomo
    "CON_ZN": 7.9,     # Zinc
    "CON_V": 0.7,      # Vanadio
    "CON_CR": 1.4,     # Cromo
    "CON_CO": 35.6,    # Cobalto (alto, pero es objetivo del proyecto)
    "CON_NI": 15.0,    # Niquel
    "CON_MO": 26.7,    # Molibdeno
    "CON_NB": 40.9,    # Niobio
    "CON_SB": 25.0,    # Antimonio
    "CON_SN": 43.1,    # Estano
    "CON_W": 79.3,     # Wolframio
    "CON_BI": 91.7,    # Bismuto
    "CON_TA": 17.4,    # Tantalio
    "CON_SC": 9.4,     # Escandio
    "CON_U": 0.3,      # Uranio
    "CON_TH": 0.1,     # Torio
    "CON_AG": 12.4,    # Plata
    "CON_AU": 69.3,    # Oro
    "CON_AS": 68.6,    # Arsenico
    "CON_CD": 20.2,    # Cadmio
    "CON_HG": 14.4,    # Mercurio
    "CON_RB": 1.0,     # Rubidio
    "CON_SR": 6.4,     # Estroncio
    "CON_Y": 23.3,     # Itrio
    "CON_ZR": 0.6,     # Circonio
    "CON_BA": 11.7,    # Bario
    "CON_CS": 0.1,     # Cesio
    "CON_HF": 0.2,     # Hafnio
    # Tierras raras (todas < 1% de censura)
    "CON_LA": 0.2, "CON_CE": 0.0, "CON_PR": 0.0, "CON_ND": 0.0,
    "CON_SM": 0.0, "CON_EU": 0.0, "CON_GD": 0.0, "CON_TB": 0.0,
    "CON_DY": 0.0, "CON_HO": 0.0, "CON_ER": 0.0, "CON_TM": 0.0,
    "CON_YB": 0.0, "CON_LU": 0.1,
}


def clasificar_fiabilidad(censura):
    """Clasifica elementos por tasa de censura."""
    if censura < 10:
        return "ALTA"
    elif censura < 30:
        return "MEDIA"
    else:
        return "BAJA"


# ------------------------------------------------------------
# 1. CARGAR ARCHIVO MAESTRO
# ------------------------------------------------------------
print("=" * 75)
print("ANALISIS DE ENRIQUECIMIENTO - ELEMENTOS FIABLES")
print("=" * 75)

df = pd.read_csv(os.path.join(OUT_DIR, "maestro_relaves.csv"))
df = df.copy()
print(f"\nDepositos: {len(df)}")

# ------------------------------------------------------------
# 2. CLASIFICAR ELEMENTOS POR FIABILIDAD
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("CLASIFICACION DE ELEMENTOS POR FIABILIDAD")
print("=" * 75)

grupos = {"ALTA": [], "MEDIA": [], "BAJA": []}
for elem, cens in CENSURA.items():
    grupos[clasificar_fiabilidad(cens)].append((elem, cens))

for grupo, elementos in grupos.items():
    print(f"\n--- {grupo} FIABILIDAD ({len(elementos)} elementos) ---")
    for elem, cens in sorted(elementos, key=lambda x: x[1]):
        nombre = elem.replace("CON_", "")
        print(f"  {nombre:<5} | censura: {cens:.1f}%")

# ------------------------------------------------------------
# 3. CALCULAR EF CON MEDIANA (mas robusta ante censura)
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("CALCULANDO EF CON MEDIANA (mas robusta)")
print("=" * 75)

CORTEZA = {
    "CON_CU": 28.0, "CON_ZN": 67.0, "CON_PB": 17.0, "CON_NI": 47.0,
    "CON_CO": 17.3, "CON_MO": 1.1, "CON_SN": 2.1,
    "CON_V": 107.0, "CON_CR": 92.0, "CON_W": 1.4, "CON_TA": 0.9,
    "CON_NB": 12.0, "CON_SB": 0.4, "CON_BI": 0.16, "CON_SC": 14.0,
    "CON_U": 2.7, "CON_TH": 10.5,
    "CON_LA": 20.0, "CON_CE": 43.0, "CON_PR": 5.1, "CON_ND": 20.0,
    "CON_SM": 3.9, "CON_EU": 0.8, "CON_GD": 3.7, "CON_TB": 0.65,
    "CON_DY": 3.5, "CON_HO": 0.8, "CON_ER": 2.3, "CON_TM": 0.33,
    "CON_YB": 2.2, "CON_LU": 0.32,
    "CON_RB": 84.0, "CON_SR": 320.0, "CON_Y": 21.0, "CON_ZR": 193.0,
    "CON_BA": 628.0, "CON_CS": 4.9, "CON_HF": 5.3,
    "CON_AS": 4.8, "CON_CD": 0.09, "CON_HG": 0.05, "CON_AG": 0.053,
    "CON_AU": 0.0015,
}

nuevas = {}
for elem, corteza in CORTEZA.items():
    col_med = f"{elem}_med"
    if col_med in df.columns:
        nuevas[f"EFmed_{elem.replace('CON_', '')}"] = df[col_med] / corteza

df_ef = pd.concat([df, pd.DataFrame(nuevas, index=df.index)], axis=1)

# ------------------------------------------------------------
# 4. RANKINGS SOLO PARA ALTA Y MEDIA FIABILIDAD
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("TOP 5 POR ELEMENTO (solo ALTA y MEDIA fiabilidad)")
print("=" * 75)

elementos_fiables = grupos["ALTA"] + grupos["MEDIA"]

for elem, cens in sorted(elementos_fiables, key=lambda x: x[1]):
    col_ef = f"EFmed_{elem.replace('CON_', '')}"
    if col_ef not in df_ef.columns:
        continue
    
    top5 = df_ef.dropna(subset=[col_ef]).nlargest(5, col_ef)
    nombre = elem.replace("CON_", "")
    fiab = clasificar_fiabilidad(cens)
    print(f"\n--- {nombre} (censura {cens:.1f}%, fiabilidad {fiab}) ---")
    for i, (_, row) in enumerate(top5.iterrows(), 1):
        faena = str(row["cat_nombre_faena"])[:32]
        print(f"  {i}. {faena:<34} EF={row[col_ef]:.2f}")

# ------------------------------------------------------------
# 5. RANKING COMBINADO DE TIERRAS RARAS
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("TOP 15 DEPOSITOS POR TIERRAS RARAS (mediana, EF promedio)")
print("=" * 75)

columnas_ree = [
    f"EFmed_{e.replace('CON_', '')}" for e in [
        "CON_LA", "CON_CE", "CON_PR", "CON_ND", "CON_SM", "CON_EU",
        "CON_GD", "CON_TB", "CON_DY", "CON_HO", "CON_ER", "CON_TM",
        "CON_YB", "CON_LU",
    ]
]
columnas_ree = [c for c in columnas_ree if c in df_ef.columns]

df_ef["EFmed_REE_avg"] = df_ef[columnas_ree].mean(axis=1)
top_ree = df_ef.dropna(subset=["EFmed_REE_avg"]).nlargest(15, "EFmed_REE_avg")

for i, (_, row) in enumerate(top_ree.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:36]
    conf = row["confiabilidad"]
    print(f"  {i:>2}. {faena:<38} EF_REE={row['EFmed_REE_avg']:.2f} [{conf}]")

# ------------------------------------------------------------
# 6. DEPOSITOS MULTI-ELEMENTO (solo fiables)
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("DEPOSITOS CON MULTIPLES ELEMENTOS ENRIQUECIDOS (solo fiables, EF>2)")
print("=" * 75)

# Solo usar elementos fiables (alta + media)
cols_fiables = [
    f"EFmed_{e.replace('CON_', '')}"
    for e, c in elementos_fiables
    if f"EFmed_{e.replace('CON_', '')}" in df_ef.columns
]

# Excluir Co porque tiene censura alta y es muy abundante
cols_sin_co = [c for c in cols_fiables if c != "EFmed_CO"]

df_ef["n_fiables_enriquecidos"] = (df_ef[cols_sin_co] > 2).sum(axis=1)
df_ef["n_ree_enriquecidos"] = (df_ef[columnas_ree] > 2).sum(axis=1)

print(f"\nDepositos con >= 3 elementos fiables enriquecidos (sin Co): {(df_ef['n_fiables_enriquecidos'] >= 3).sum()}")
print(f"Depositos con >= 5 elementos fiables enriquecidos (sin Co): {(df_ef['n_fiables_enriquecidos'] >= 5).sum()}")
print(f"Depositos con >= 8 elementos fiables enriquecidos (sin Co): {(df_ef['n_fiables_enriquecidos'] >= 8).sum()}")

print(f"\nDepositos con >= 5 REE enriquecidas: {(df_ef['n_ree_enriquecidos'] >= 5).sum()}")
print(f"Depositos con >= 10 REE enriquecidas: {(df_ef['n_ree_enriquecidos'] >= 10).sum()}")

# Top 15 multi-elemento
print("\nTop 15 depositos multi-elemento (elementos fiables sin Co):")
top_multi = df_ef.nlargest(15, "n_fiables_enriquecidos")[
    ["cat_id", "cat_nombre_faena", "n_fiables_enriquecidos", "n_ree_enriquecidos", "confiabilidad"]
]
print(top_multi.to_string(index=False))

# ------------------------------------------------------------
# 7. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "maestro_con_ef_fiable.csv")
df_ef.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo guardado en: {ruta}")
print(f"  Dimensiones: {df_ef.shape[0]} filas x {df_ef.shape[1]} columnas")
