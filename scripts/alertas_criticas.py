# ============================================================
# SISTEMA DE ALERTAS CRITICAS
# Anade columnas booleanas de alerta al ranking de riesgo
# ============================================================

import pandas as pd
import numpy as np
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

print("=" * 75)
print("SISTEMA DE ALERTAS CRITICAS")
print("=" * 75)

# ------------------------------------------------------------
# 1. CARGAR
# ------------------------------------------------------------
df = pd.read_csv(os.path.join(OUT_DIR, "ranking_con_riesgo.csv"))
df = df.copy()  # Desfragmentar
print(f"\nDepositos: {len(df)}")

# ------------------------------------------------------------
# 2. CREAR ALERTAS (todas a la vez para evitar fragmentacion)
# ------------------------------------------------------------
print("\nGenerando alertas...")

alertas = pd.DataFrame(index=df.index)

# Alerta 1: Metodo aguas arriba (prohibido en Chile desde 1970)
alertas["ALERTA_AGUAS_ARRIBA"] = (
    df["METODO_CONSTRUCTIVO_MURO"].fillna("").str.upper().str.contains("AGUAS ARRIBA")
)

# Alerta 2: Estado abandonado (sin responsable legal)
alertas["ALERTA_ABANDONADO"] = (
    df["cat_estado"].fillna("").str.upper() == "ABANDONADO"
)

# Alerta 3: Sin metodo constructivo registrado (desconocimiento)
alertas["ALERTA_SIN_METODO"] = (
    df["METODO_CONSTRUCTIVO_MURO"].isna() |
    (df["METODO_CONSTRUCTIVO_MURO"].fillna("").str.strip() == "")
)

# Alerta 4: Exposicion MUY_ALTA (<500 m de poblado)
alertas["ALERTA_EXPOSICION_MUY_ALTA"] = (
    df["exposicion_poblados"] == "MUY_ALTA"
)

# Alerta 5: Exposicion ALTA (500 m - 2 km)
alertas["ALERTA_EXPOSICION_ALTA"] = (
    df["exposicion_poblados"] == "ALTA"
)

# Alerta 6: Tonelaje catastrofico (>1000 Mt)
alertas["ALERTA_TONELAJE_CATASTROFICO"] = (
    df["cat_tonelaje_autorizado"].fillna(0) >= 1_000_000_000
)

# Alerta 7: Tonelaje muy alto (100-1000 Mt)
alertas["ALERTA_TONELAJE_MUY_ALTO"] = (
    (df["cat_tonelaje_autorizado"].fillna(0) >= 100_000_000) &
    (df["cat_tonelaje_autorizado"].fillna(0) < 1_000_000_000)
)

# Agregar todas las alertas de una vez
df = pd.concat([df, alertas], axis=1)

# ------------------------------------------------------------
# 3. CONTAR ALERTAS Y CREAR LISTA
# ------------------------------------------------------------
columnas_alerta = [c for c in df.columns if c.startswith("ALERTA_")]

df["n_alertas"] = df[columnas_alerta].sum(axis=1)

def listar_alertas(row):
    activas = [c.replace("ALERTA_", "") for c in columnas_alerta if row[c]]
    return ", ".join(activas) if activas else "NINGUNA"

df["alertas_activas"] = df.apply(listar_alertas, axis=1)

# ------------------------------------------------------------
# 4. REPORTE
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("DISTRIBUCION DE ALERTAS")
print("=" * 75)

for col in columnas_alerta:
    cant = df[col].sum()
    pct = 100 * cant / len(df)
    nombre = col.replace("ALERTA_", "")
    print(f"  {nombre:<30}: {cant:>3} ({pct:.1f}%)")

print(f"\nDistribucion de numero de alertas por deposito:")
for n in sorted(df["n_alertas"].unique(), reverse=True):
    cant = (df["n_alertas"] == n).sum()
    pct = 100 * cant / len(df)
    print(f"  {n} alertas: {cant:>3} ({pct:.1f}%)")

# ------------------------------------------------------------
# 5. TOP 20 CON MAS ALERTAS
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("TOP 20 DEPOSITOS CON MAS ALERTAS CRITICAS")
print("=" * 75)

top = df.nlargest(20, "n_alertas")[
    ["cat_id", "cat_nombre_faena", "cat_tonelaje_autorizado",
     "n_alertas", "indice_riesgo", "nivel_riesgo", "alertas_activas"]
].copy()
top["tonelaje_Mt"] = (top["cat_tonelaje_autorizado"] / 1e6).round(1)

print(f"\n{'#':<3} {'ID':<11} {'Faena':<30} {'Mt':>7} {'Alertas':<50}")
print("-" * 110)
for i, (_, row) in enumerate(top.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:28]
    alertas = str(row["alertas_activas"])[:48]
    print(f"{i:<3} {row['cat_id']:<11} {faena:<30} {row['tonelaje_Mt']:>7.1f} {alertas:<50}")

# ------------------------------------------------------------
# 6. CRUCE: ALERTAS x NIVEL DE RIESGO
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("CRUCE: NIVEL DE RIESGO x NUMERO DE ALERTAS")
print("=" * 75)

cruce = pd.crosstab(df["nivel_riesgo"], df["n_alertas"], margins=True)
print(cruce.to_string())

# ------------------------------------------------------------
# 7. CASOS ESPECIALES (alertas criticas especificas)
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("CASOS ESPECIALES")
print("=" * 75)

# Aguas arriba + abandonado
caso1 = df[df["ALERTA_AGUAS_ARRIBA"] & df["ALERTA_ABANDONADO"]]
print(f"\n--- AGUAS ARRIBA + ABANDONADO ({len(caso1)} casos) ---")
if len(caso1) > 0:
    for _, row in caso1.iterrows():
        print(f"  {row['cat_id']:<11} {str(row['cat_nombre_faena'])[:40]:<42} {row['cat_tonelaje_autorizado']/1e6:.1f} Mt")

# Aguas arriba + exposicion alta/muy alta
caso2 = df[df["ALERTA_AGUAS_ARRIBA"] &
           (df["ALERTA_EXPOSICION_ALTA"] | df["ALERTA_EXPOSICION_MUY_ALTA"])]
print(f"\n--- AGUAS ARRIBA + EXPOSICION ALTA/MUY ALTA ({len(caso2)} casos) ---")
if len(caso2) > 0:
    for _, row in caso2.iterrows():
        print(f"  {row['cat_id']:<11} {str(row['cat_nombre_faena'])[:38]:<40} dist={row['distancia_caserio_m']:.0f} m")

# Sin metodo + abandonado
caso3 = df[df["ALERTA_SIN_METODO"] & df["ALERTA_ABANDONADO"]]
print(f"\n--- SIN METODO + ABANDONADO ({len(caso3)} casos) ---")
if len(caso3) > 0:
    for _, row in caso3.iterrows():
        print(f"  {row['cat_id']:<11} {str(row['cat_nombre_faena'])[:40]:<42} {row['cat_tonelaje_autorizado']/1e6:.1f} Mt")

# ------------------------------------------------------------
# 8. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "ranking_con_alertas.csv")
df.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo guardado en: {ruta}")
print(f"  Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")