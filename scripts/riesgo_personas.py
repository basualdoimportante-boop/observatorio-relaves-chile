# ============================================================
# ANALISIS DE RIESGO A PERSONAS
# Depositos que amenazan directamente a comunidades
# ============================================================

import pandas as pd
import numpy as np
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

print("=" * 75)
print("ANALISIS DE RIESGO A PERSONAS")
print("=" * 75)

df = pd.read_csv(os.path.join(OUT_DIR, "ranking_final_integrado.csv"))
df = df.copy()
print(f"\nDepositos totales: {len(df)}")

# ------------------------------------------------------------
# 1. FILTRAR DEPOSITOS CON EXPOSICION A POBLADOS
# ------------------------------------------------------------
print("\n[1] Identificando depositos con exposicion a poblados...")

# Depositos con exposicion ALTA o MUY_ALTA
con_exposicion = df[df["exposicion_poblados"].isin(["ALTA", "MUY_ALTA"])].copy()
print(f"  Depositos con exposicion ALTA o MUY_ALTA: {len(con_exposicion)}")

# ------------------------------------------------------------
# 2. CALCULAR INDICE DE RIESGO A PERSONAS
# ------------------------------------------------------------
print("\n[2] Calculando indice de riesgo a personas...")

# Factores de riesgo a personas
def calcular_riesgo_personas(row):
    puntaje = 0
    
    # Factor 1: Distancia al poblado
    dist = row["distancia_caserio_m"]
    if pd.notna(dist):
        if dist < 500:
            puntaje += 4  # Muy cerca
        elif dist < 1000:
            puntaje += 3
        elif dist < 2000:
            puntaje += 2
        else:
            puntaje += 1
    
    # Factor 2: Poblacion del caserio
    pob = row.get("caserio_poblacion", 0)
    if pd.notna(pob):
        if pob >= 500:
            puntaje += 4
        elif pob >= 100:
            puntaje += 3
        elif pob >= 50:
            puntaje += 2
        elif pob >= 1:
            puntaje += 1
    
    # Factor 3: Metodo constructivo
    metodo = str(row["METODO_CONSTRUCTIVO_MURO"]).upper()
    if "AGUAS ARRIBA" in metodo:
        puntaje += 4
    elif "EJE CENTRAL" in metodo:
        puntaje += 2
    elif metodo in ["NAN", "NONE", ""]:
        puntaje += 3  # Precaución por desconocimiento
    
    # Factor 4: Estado
    estado = str(row["cat_estado"]).upper()
    if estado == "ABANDONADO":
        puntaje += 3
    elif estado == "INACTIVO":
        puntaje += 1
    
    # Factor 5: Antiguedad
    antig = row.get("antiguedad_anios", 0)
    if pd.notna(antig) and antig >= 40:
        puntaje += 2
    elif pd.notna(antig) and antig >= 20:
        puntaje += 1
    
    # Factor 6: Amenaza sismica
    sa = row.get("SA_0_3_02", 0)
    if pd.notna(sa):
        if sa >= 1.8:
            puntaje += 3
        elif sa >= 1.3:
            puntaje += 2
        elif sa >= 0.8:
            puntaje += 1
    
    # Factor 7: Precipitacion extrema
    precip = row.get("precip_max_diaria_hist", 0)
    if pd.notna(precip):
        if precip >= 100:
            puntaje += 3
        elif precip >= 70:
            puntaje += 2
        elif precip >= 50:
            puntaje += 1
    
    return puntaje

con_exposicion["riesgo_personas"] = con_exposicion.apply(calcular_riesgo_personas, axis=1)

# Clasificar
def clasificar_riesgo_personas(puntaje):
    if puntaje >= 15:
        return "CRITICO"
    elif puntaje >= 11:
        return "MUY_ALTO"
    elif puntaje >= 8:
        return "ALTO"
    elif puntaje >= 5:
        return "MEDIO"
    else:
        return "BAJO"

con_exposicion["nivel_riesgo_personas"] = con_exposicion["riesgo_personas"].apply(clasificar_riesgo_personas)

# ------------------------------------------------------------
# 3. REPORTE
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("DISTRIBUCION DE RIESGO A PERSONAS")
print("=" * 75)

for nivel in ["CRITICO", "MUY_ALTO", "ALTO", "MEDIO", "BAJO"]:
    cant = (con_exposicion["nivel_riesgo_personas"] == nivel).sum()
    pct = 100 * cant / len(con_exposicion)
    print(f"  {nivel:<10}: {cant:>3} ({pct:.1f}%)")

# ------------------------------------------------------------
# 4. TOP: DEPOSITOS CON MAYOR RIESGO A PERSONAS
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("DEPOSITOS CON RIESGO CRITICO A PERSONAS")
print("=" * 75)

criticos = con_exposicion[con_exposicion["nivel_riesgo_personas"] == "CRITICO"].sort_values(
    "riesgo_personas", ascending=False
)

print(f"\nTotal: {len(criticos)}")
print(f"\n{'#':<3} {'ID':<11} {'Faena':<28} {'Mt':>7} {'Dist(m)':>8} {'Caserio':<22} {'Pob':>5} {'Riesgo':>6}")
print("-" * 110)
for i, (_, row) in enumerate(criticos.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:26]
    mt = row["cat_tonelaje_autorizado"] / 1e6 if pd.notna(row["cat_tonelaje_autorizado"]) else 0
    dist = row["distancia_caserio_m"]
    caserio = str(row.get("caserio_nombre", ""))[:20]
    pob = int(row.get("caserio_poblacion", 0)) if pd.notna(row.get("caserio_poblacion", 0)) else 0
    print(f"{i:<3} {row['cat_id']:<11} {faena:<28} {mt:>7.1f} {dist:>8.0f} {caserio:<22} {pob:>5} {row['riesgo_personas']:>6}")

# ------------------------------------------------------------
# 5. LISTA DETALLADA POR DEPOSITO
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("FICHAS DETALLADAS: RIESGO CRITICO Y MUY ALTO")
print("=" * 75)

prioritarios = con_exposicion[
    con_exposicion["nivel_riesgo_personas"].isin(["CRITICO", "MUY_ALTO"])
].sort_values("riesgo_personas", ascending=False)

for _, row in prioritarios.iterrows():
    print(f"\n{'='*70}")
    print(f"DEPOSITO: {row['cat_id']} - {row['cat_nombre_faena']}")
    print(f"{'='*70}")
    print(f"  Region: {row['REGION']} / Comuna: {row['COMUNA']}")
    print(f"  Empresa: {row.get('cat_nombre_empresa', 'Desconocida')}")
    print(f"  Estado: {row['cat_estado']}")
    print(f"  Metodo constructivo: {row['METODO_CONSTRUCTIVO_MURO']}")
    print(f"  Tonelaje: {row['cat_tonelaje_autorizado']/1e6:.1f} Mt" if pd.notna(row["cat_tonelaje_autorizado"]) else "  Tonelaje: No registrado")
    print(f"  Anio aprobacion: {row.get('anio_aprobacion', 'No registrado')}")
    print(f"  Antiguedad: {row.get('antiguedad_anios', 'N/A')} anios")
    print(f"  ---")
    print(f"  Caserio mas cercano: {row.get('caserio_nombre', 'Sin dato')}")
    print(f"  Poblacion: {int(row.get('caserio_poblacion', 0)) if pd.notna(row.get('caserio_poblacion')) else 'Sin dato'} personas")
    print(f"  Distancia: {row['distancia_caserio_m']:.0f} metros")
    print(f"  ---")
    print(f"  Amenaza sismica (SA 0.3): {row['SA_0_3_02']:.2f}g")
    print(f"  Precipitacion max diaria: {row['precip_max_diaria_hist']:.0f} mm")
    print(f"  ---")
    print(f"  RIESGO A PERSONAS: {row['riesgo_personas']} puntos ({row['nivel_riesgo_personas']})")
    print(f"  Alertas activas: {row['alertas_activas']}")
    print(f"  Indice riesgo general: {row['indice_riesgo']}")
    print(f"  Categoria de decision: {row['categoria_decision']}")

# ------------------------------------------------------------
# 6. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "riesgo_personas.csv")
con_exposicion.to_csv(ruta, index=False, encoding="utf-8")
print(f"\n\nArchivo guardado en: {ruta}")
print(f"  Depositos con exposicion: {len(con_exposicion)}")
print(f"  Criticos: {len(criticos)}")
print(f"  Muy altos: {(con_exposicion['nivel_riesgo_personas'] == 'MUY_ALTO').sum()}")