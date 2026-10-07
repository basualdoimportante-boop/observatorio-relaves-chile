# ============================================================
# RANKING INTEGRADO FINAL
# Combina: potencial economico + riesgo estructural + amenaza sismica
# Matriz de decision con 4 categorias
# ============================================================

import pandas as pd
import numpy as np
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

print("=" * 75)
print("RANKING INTEGRADO FINAL")
print("=" * 75)

# ------------------------------------------------------------
# 1. CARGAR DATOS
# ------------------------------------------------------------
df = pd.read_csv(os.path.join(OUT_DIR, "ranking_final_completo.csv"))
df = df.copy()
print(f"\nDepositos: {len(df)}")

# ------------------------------------------------------------
# 2. RECALIBRAR AMENAZA SISMICA CON UMBRALES CHILENOS
# ------------------------------------------------------------
print("\n[1] Recalibrando amenaza sismica...")

def clasificar_sa03_recalibrado(valor):
    """Umbrales calibrados para la realidad sismica chilena."""
    if pd.isna(valor):
        return "DESCONOCIDA"
    elif valor >= 1.8:
        return "MUY_ALTA"
    elif valor >= 1.3:
        return "ALTA"
    elif valor >= 0.8:
        return "MEDIA"
    elif valor >= 0.4:
        return "BAJA"
    else:
        return "MUY_BAJA"

df["nivel_amenaza_recalibrado"] = df["SA_0_3_02"].apply(clasificar_sa03_recalibrado)

print("Distribucion recalibrada:")
for nivel in ["MUY_ALTA", "ALTA", "MEDIA", "BAJA", "MUY_BAJA"]:
    cant = (df["nivel_amenaza_recalibrado"] == nivel).sum()
    pct = 100 * cant / len(df)
    print(f"  {nivel:<12}: {cant:>3} ({pct:.1f}%)")

# ------------------------------------------------------------
# 3. RECALCULAR ALERTAS SISMICAS
# ------------------------------------------------------------
print("\n[2] Recalculando alertas sismicas...")

# Eliminar las alertas anteriores (estaban mal calibradas)
df = df.drop(columns=["ALERTA_SISMICA_MUY_ALTA", "ALERTA_SISMICA_ALTA", "ALERTA_SISMICA_CRITICA"])

# Nuevas alertas
df["ALERTA_SISMICA_MUY_ALTA"] = df["SA_0_3_02"] >= 1.8
df["ALERTA_SISMICA_ALTA"] = (df["SA_0_3_02"] >= 1.3) & (df["SA_0_3_02"] < 1.8)
df["ALERTA_SISMICA_CRITICA"] = (
    (df["SA_0_3_02"] >= 1.3) &
    (df["antiguedad_anios"] >= 30)
)

# Recalcular contador
columnas_alerta = [c for c in df.columns if c.startswith("ALERTA_")]
df["n_alertas"] = df[columnas_alerta].sum(axis=1)

def listar_alertas(row):
    activas = [c.replace("ALERTA_", "") for c in columnas_alerta if row[c]]
    return ", ".join(activas) if activas else "NINGUNA"

df["alertas_activas"] = df.apply(listar_alertas, axis=1)

print(f"  SISMICA_MUY_ALTA: {df['ALERTA_SISMICA_MUY_ALTA'].sum()}")
print(f"  SISMICA_ALTA: {df['ALERTA_SISMICA_ALTA'].sum()}")
print(f"  SISMICA_CRITICA: {df['ALERTA_SISMICA_CRITICA'].sum()}")

# ------------------------------------------------------------
# 4. CALCULAR POTENCIAL ECONOMICO
# ------------------------------------------------------------
print("\n[3] Calculando potencial economico...")

# Elementos de alto valor para el analisis
# Solo elementos fiables (censura <10%)
ELEMENTOS_CLAVE = ["CU", "ZN", "PB", "V", "CS", "RB", "SC", "U"]

# Sumar cuantos elementos clave tienen EF > 2
columnas_ef = [f"EF_{e}" for e in ELEMENTOS_CLAVE if f"EF_{e}" in df.columns]
df["n_elementos_clave_enriquecidos"] = (df[columnas_ef] > 2).sum(axis=1)

# Tierras raras
cols_ree = [c for c in df.columns if c.startswith("EF_") and any(
    ree in c for ree in ["LA", "CE", "PR", "ND", "SM", "EU", "GD", "TB", "DY", "HO", "ER", "TM", "YB", "LU"]
)]
df["n_ree_enriquecidas"] = (df[cols_ree] > 2).sum(axis=1)

# Potencial total = elementos clave + tierras raras
df["potencial_total"] = df["n_elementos_clave_enriquecidos"] + df["n_ree_enriquecidas"]

# Clasificar potencial
def clasificar_potencial(n):
    if n >= 5:
        return "MUY_ALTO"
    elif n >= 3:
        return "ALTO"
    elif n >= 1:
        return "MEDIO"
    else:
        return "BAJO"

df["nivel_potencial"] = df["potencial_total"].apply(clasificar_potencial)

print("Distribucion de potencial:")
for nivel in ["MUY_ALTO", "ALTO", "MEDIO", "BAJO"]:
    cant = (df["nivel_potencial"] == nivel).sum()
    pct = 100 * cant / len(df)
    print(f"  {nivel:<10}: {cant:>3} ({pct:.1f}%)")

# ------------------------------------------------------------
# 5. MATRIZ DE DECISION
# ------------------------------------------------------------
print("\n[4] Generando matriz de decision...")

def matriz_decision(row):
    """Combina potencial y riesgo en 4 categorias."""
    potencial_alto = row["nivel_potencial"] in ["MUY_ALTO", "ALTO"]
    riesgo_alto = (row["indice_riesgo"] >= 5) or (row["n_alertas"] >= 4)
    
    if potencial_alto and riesgo_alto:
        return "PRIORIDAD_MAXIMA"
    elif not potencial_alto and riesgo_alto:
        return "PRIORIDAD_REMEDIACION"
    elif potencial_alto and not riesgo_alto:
        return "PRIORIDAD_ECONOMICA"
    else:
        return "BAJA_PRIORIDAD"

df["categoria_decision"] = df.apply(matriz_decision, axis=1)

print("\nDistribucion de la matriz de decision:")
for cat in ["PRIORIDAD_MAXIMA", "PRIORIDAD_REMEDIACION", "PRIORIDAD_ECONOMICA", "BAJA_PRIORIDAD"]:
    cant = (df["categoria_decision"] == cat).sum()
    pct = 100 * cant / len(df)
    print(f"  {cat:<25}: {cant:>3} ({pct:.1f}%)")

# ------------------------------------------------------------
# 6. REPORTE: TOP 20 PRIORIDAD MAXIMA
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("PRIORIDAD MAXIMA: ALTO POTENCIAL + ALTO RIESGO")
print("=" * 75)

maxima = df[df["categoria_decision"] == "PRIORIDAD_MAXIMA"].sort_values(
    "indice_riesgo", ascending=False
)

print(f"\nTotal: {len(maxima)}")
print(f"\n{'ID':<11} {'Faena':<28} {'Mt':>7} {'Pot':>4} {'Riesgo':>6} {'Alert':>5} {'Categoria':<20}")
print("-" * 95)
for _, row in maxima.iterrows():
    faena = str(row["cat_nombre_faena"])[:26]
    mt = row["cat_tonelaje_autorizado"] / 1e6 if pd.notna(row["cat_tonelaje_autorizado"]) else 0
    print(f"{row['cat_id']:<11} {faena:<28} {mt:>7.1f} {row['potencial_total']:>4} {row['indice_riesgo']:>6} {row['n_alertas']:>5} {row['categoria_decision']:<20}")

# ------------------------------------------------------------
# 7. REPORTE: TOP 20 PRIORIDAD REMEDIACION
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("PRIORIDAD REMEDIACION: ALTO RIESGO SIN POTENCIAL ECONOMICO")
print("=" * 75)

remediacion = df[df["categoria_decision"] == "PRIORIDAD_REMEDIACION"].sort_values(
    "n_alertas", ascending=False
)

print(f"\nTotal: {len(remediacion)}")
print(f"\n{'ID':<11} {'Faena':<28} {'Mt':>7} {'Alert':>5} {'Índ':>4} {'Alertas activas':<50}")
print("-" * 110)
for _, row in remediacion.head(20).iterrows():
    faena = str(row["cat_nombre_faena"])[:26]
    mt = row["cat_tonelaje_autorizado"] / 1e6 if pd.notna(row["cat_tonelaje_autorizado"]) else 0
    alertas = str(row["alertas_activas"])[:48]
    print(f"{row['cat_id']:<11} {faena:<28} {mt:>7.1f} {row['n_alertas']:>5} {row['indice_riesgo']:>4} {alertas:<50}")

# ------------------------------------------------------------
# 8. REPORTE: TOP 20 PRIORIDAD ECONOMICA
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("PRIORIDAD ECONOMICA: ALTO POTENCIAL SIN RIESGO ALTO")
print("=" * 75)

economica = df[df["categoria_decision"] == "PRIORIDAD_ECONOMICA"].sort_values(
    "potencial_total", ascending=False
)

print(f"\nTotal: {len(economica)}")
print(f"\n{'ID':<11} {'Faena':<28} {'Mt':>7} {'Pot':>4} {'REE':>4} {'Índ':>4}")
print("-" * 75)
for _, row in economica.head(20).iterrows():
    faena = str(row["cat_nombre_faena"])[:26]
    mt = row["cat_tonelaje_autorizado"] / 1e6 if pd.notna(row["cat_tonelaje_autorizado"]) else 0
    print(f"{row['cat_id']:<11} {faena:<28} {mt:>7.1f} {row['potencial_total']:>4} {row['n_ree_enriquecidas']:>4} {row['indice_riesgo']:>4}")

# ------------------------------------------------------------
# 9. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "ranking_final_integrado.csv")
df.to_csv(ruta, index=False, encoding="utf-8")
print(f"\n\nArchivo guardado en: {ruta}")
print(f"  Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")