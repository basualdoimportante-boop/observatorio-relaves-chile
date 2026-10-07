# ============================================================
# PROCESAR DATOS DE PRECIPITACION
# Agrega los 10 anios y cruza con el ranking de riesgo
# ============================================================

import pandas as pd
import numpy as np
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

print("=" * 75)
print("PROCESAMIENTO DE DATOS DE PRECIPITACION")
print("=" * 75)

# ------------------------------------------------------------
# 1. CARGAR EL CSV DE PRECIPITACION
# ------------------------------------------------------------
print("\n[1] Cargando datos de precipitacion...")

df_precip = pd.read_csv(os.path.join(DATA_DIR, "precipitacion_relaves_v2.csv"))
print(f"  Registros: {len(df_precip)}")
print(f"  Columnas: {df_precip.columns.tolist()}")
print(f"  Depositos unicos: {df_precip['id'].nunique()}")
print(f"  Anios: {sorted(df_precip['anio'].unique())}")

# ------------------------------------------------------------
# 2. AGREGAR POR DEPOSITO
# ------------------------------------------------------------
print("\n[2] Agregando por deposito...")

resumen = df_precip.groupby("id").agg(
    precip_promedio_anual=("precip_total_anual", "mean"),
    precip_max_anual=("precip_total_anual", "max"),
    precip_max_diaria_hist=("precip_max_diaria", "max"),
    precip_promedio_max_diaria=("precip_max_diaria", "mean"),
    dias_extremos_total=("dias_mayor_50mm", "sum"),
    anios_registrados=("anio", "count"),
).reset_index()

resumen = resumen.rename(columns={"id": "cat_id"})

print(f"  Depositos con resumen: {len(resumen)}")

# ------------------------------------------------------------
# 3. CLASIFICAR POR NIVEL DE PRECIPITACION
# ------------------------------------------------------------
def clasificar_precipitacion(precip_anual):
    """Clasifica segun precipitacion anual promedio (mm)."""
    if precip_anual >= 1500:
        return "MUY_ALTA"    # Zona muy lluviosa
    elif precip_anual >= 800:
        return "ALTA"        # Zona lluviosa
    elif precip_anual >= 400:
        return "MEDIA"       # Zona mediterranea
    elif precip_anual >= 100:
        return "BAJA"        # Zona semiarida
    else:
        return "MUY_BAJA"    # Zona arida

resumen["nivel_precipitacion"] = resumen["precip_promedio_anual"].apply(clasificar_precipitacion)

def clasificar_eventos_extremos(max_diaria):
    """Clasifica segun evento maximo diario."""
    if max_diaria >= 100:
        return "EXTREMO"     # Evento >100 mm/dia
    elif max_diaria >= 70:
        return "ALTO"        # Evento >70 mm/dia
    elif max_diaria >= 50:
        return "MEDIO"
    else:
        return "BAJO"

resumen["nivel_evento_extremo"] = resumen["precip_max_diaria_hist"].apply(clasificar_eventos_extremos)

# ------------------------------------------------------------
# 4. CARGAR RANKING DE RIESGO
# ------------------------------------------------------------
print("\n[3] Cargando ranking de riesgo...")

df_riesgo = pd.read_csv(os.path.join(OUT_DIR, "ranking_con_alertas.csv"))
df_riesgo = df_riesgo.copy()

# Unir
df_final = df_riesgo.merge(resumen, on="cat_id", how="left")
print(f"  Depositos en el cruce: {len(df_final)}")
print(f"  Con datos de precipitacion: {df_final['precip_promedio_anual'].notna().sum()}")

# ------------------------------------------------------------
# 5. NUEVAS ALERTAS DE PRECIPITACION
# ------------------------------------------------------------
print("\n[4] Generando alertas de precipitacion...")

df_final["ALERTA_PRECIP_EXTREMA"] = df_final["precip_max_diaria_hist"] >= 100
df_final["ALERTA_PRECIP_ALTA"] = (
    (df_final["precip_max_diaria_hist"] >= 70) &
    (df_final["precip_max_diaria_hist"] < 100)
)
df_final["ALERTA_ZONA_LLUVIOSA"] = df_final["precip_promedio_anual"] >= 800

# Actualizar contador de alertas
columnas_alerta = [c for c in df_final.columns if c.startswith("ALERTA_")]

df_final["n_alertas"] = df_final[columnas_alerta].sum(axis=1)

def listar_alertas(row):
    activas = [c.replace("ALERTA_", "") for c in columnas_alerta if row[c]]
    return ", ".join(activas) if activas else "NINGUNA"

df_final["alertas_activas"] = df_final.apply(listar_alertas, axis=1)

# ------------------------------------------------------------
# 6. REPORTE
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("RESULTADOS DE PRECIPITACION")
print("=" * 75)

print("\nDistribucion por nivel de precipitacion anual:")
for nivel in ["MUY_ALTA", "ALTA", "MEDIA", "BAJA", "MUY_BAJA"]:
    cant = (df_final["nivel_precipitacion"] == nivel).sum()
    pct = 100 * cant / len(df_final)
    print(f"  {nivel:<12}: {cant:>3} ({pct:.1f}%)")

print("\nDistribucion por evento extremo maximo:")
for nivel in ["EXTREMO", "ALTO", "MEDIO", "BAJO"]:
    cant = (df_final["nivel_evento_extremo"] == nivel).sum()
    pct = 100 * cant / len(df_final)
    print(f"  {nivel:<12}: {cant:>3} ({pct:.1f}%)")

print(f"\nDepositos con evento >100 mm/dia: {df_final['ALERTA_PRECIP_EXTREMA'].sum()}")
print(f"Depositos en zona muy lluviosa (>800 mm/anio): {df_final['ALERTA_ZONA_LLUVIOSA'].sum()}")

# Top 15 con mayor precipitacion extrema
print("\n" + "=" * 75)
print("TOP 15 DEPOSITOS CON EVENTO EXTREMO MAS ALTO")
print("=" * 75)

top_precip = df_final.nlargest(15, "precip_max_diaria_hist")[
    ["cat_id", "cat_nombre_faena", "cat_tonelaje_autorizado",
     "precip_max_diaria_hist", "precip_promedio_anual",
     "nivel_evento_extremo", "indice_riesgo", "alertas_activas"]
].copy()
top_precip["tonelaje_Mt"] = (top_precip["cat_tonelaje_autorizado"] / 1e6).round(1)

print(f"\n{'#':<3} {'ID':<11} {'Faena':<30} {'Mt':>7} {'MaxDiario':>10} {'PromAnual':>10} {'Índ':>4}")
print("-" * 95)
for i, (_, row) in enumerate(top_precip.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:28]
    print(f"{i:<3} {row['cat_id']:<11} {faena:<30} {row['tonelaje_Mt']:>7.1f} {row['precip_max_diaria_hist']:>10.1f} {row['precip_promedio_anual']:>10.0f} {row['indice_riesgo']:>4}")

# Top 15 con mayor precipitacion anual
print("\n" + "=" * 75)
print("TOP 15 DEPOSITOS EN ZONA MAS LLUVIOSA")
print("=" * 75)

top_lluvia = df_final.nlargest(15, "precip_promedio_anual")[
    ["cat_id", "cat_nombre_faena", "cat_tonelaje_autorizado",
     "precip_promedio_anual", "precip_max_diaria_hist", "nivel_precipitacion"]
].copy()
top_lluvia["tonelaje_Mt"] = (top_lluvia["cat_tonelaje_autorizado"] / 1e6).round(1)

print(f"\n{'#':<3} {'ID':<11} {'Faena':<30} {'Mt':>7} {'PromAnual':>10} {'MaxDiario':>10}")
print("-" * 85)
for i, (_, row) in enumerate(top_lluvia.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:28]
    print(f"{i:<3} {row['cat_id']:<11} {faena:<30} {row['tonelaje_Mt']:>7.1f} {row['precip_promedio_anual']:>10.0f} {row['precip_max_diaria_hist']:>10.1f}")

# ------------------------------------------------------------
# 7. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "ranking_con_precipitacion.csv")
df_final.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo guardado en: {ruta}")
print(f"  Dimensiones: {df_final.shape[0]} filas x {df_final.shape[1]} columnas")
