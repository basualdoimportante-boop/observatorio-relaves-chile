# ============================================================
# DIAGNOSTICO DE ANOMALIAS EN EL CRUCE
# Investiga los casos con distancia extrema y los SIN_CANDIDATO
# ============================================================

import pandas as pd
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# Cargar el resultado del cruce
df = pd.read_csv(os.path.join(OUT_DIR, "cruce_completo.csv"))

print("=" * 80)
print("DIAGNOSTICO DE ANOMALIAS")
print("=" * 80)

# ------------------------------------------------------------
# 1. TOP 20 CASOS MAS LEJANOS
# ------------------------------------------------------------
print("\n" + "=" * 80)
print("TOP 20 CASOS CON MAYOR DISTANCIA (candidatos a error)")
print("=" * 80)

top_lejos = df.nlargest(20, "distancia_m")[[
    "geoq_id", "geoq_nombre_fae", "geoq_comuna",
    "geoq_utm_norte", "geoq_utm_este",
    "cat_id", "cat_nombre_faena", "cat_nombre_instalacion",
    "distancia_m"
]]

for i, row in top_lejos.iterrows():
    print(f"\n--- Caso {i} ---")
    print(f"  Muestra geoq ID:      {row['geoq_id']}")
    print(f"  Nombre faena geoq:    {row['geoq_nombre_fae']}")
    print(f"  Comuna:               {row['geoq_comuna']}")
    print(f"  UTM geoq:             N={row['geoq_utm_norte']:.0f}  E={row['geoq_utm_este']:.0f}")
    print(f"  Deposito catastro:    {row['cat_id']} - {row['cat_nombre_faena']}")
    print(f"  Instalacion:          {row['cat_nombre_instalacion']}")
    print(f"  DISTANCIA:            {row['distancia_m']:.1f} m ({row['distancia_m']/1000:.1f} km)")

# ------------------------------------------------------------
# 2. LOS 22 CASOS SIN CANDIDATO
# ------------------------------------------------------------
print("\n\n" + "=" * 80)
print("CASOS SIN CANDIDATO (comuna no encontrada en catastro)")
print("=" * 80)

sin_cand = df[df["categoria"] == "SIN_CANDIDATO"]

print(f"\nTotal: {len(sin_cand)} muestras")
print(f"\nComunas unicas en estos casos:")
comunas_sin = sin_cand["geoq_comuna"].value_counts()
for comuna, cantidad in comunas_sin.items():
    print(f"  {comuna}: {cantidad} muestras")

print(f"\nDetalle de cada caso:")
for i, row in sin_cand.iterrows():
    print(f"  ID {row['geoq_id']}: {row['geoq_nombre_fae']} (comuna: {row['geoq_comuna']})")

# ------------------------------------------------------------
# 3. DISTRIBUCION DE DISTANCIAS POR RANGOS
# ------------------------------------------------------------
print("\n\n" + "=" * 80)
print("DISTRIBUCION DE DISTANCIAS POR RANGOS")
print("=" * 80)

con_dist = df[df["distancia_m"].notna()]

rangos = [
    (0, 100, "0-100 m"),
    (100, 500, "100-500 m"),
    (500, 1000, "500 m - 1 km"),
    (1000, 5000, "1-5 km"),
    (5000, 10000, "5-10 km"),
    (10000, 50000, "10-50 km"),
    (50000, 1000000, "> 50 km"),
]

print(f"\n{'Rango':<20} {'Cantidad':<12} {'Porcentaje':<12}")
print("-" * 50)
for min_d, max_d, nombre in rangos:
    cantidad = len(con_dist[(con_dist["distancia_m"] >= min_d) & (con_dist["distancia_m"] < max_d)])
    pct = 100 * cantidad / len(con_dist)
    print(f"{nombre:<20} {cantidad:<12} {pct:<12.2f}%")

# ------------------------------------------------------------
# 4. GUARDAR CASOS ANOMALOS PARA REVISION
# ------------------------------------------------------------
print("\n\n" + "=" * 80)
print("GUARDANDO CASOS ANOMALOS")
print("=" * 80)

# Casos con distancia > 10 km (sospechosos)
sospechosos = df[df["distancia_m"] > 10000].copy()
ruta_sospechosos = os.path.join(OUT_DIR, "casos_sospechosos.csv")
sospechosos.to_csv(ruta_sospechosos, index=False, encoding="utf-8")
print(f"\nCasos con distancia > 10 km: {len(sospechosos)}")
print(f"Guardados en: {ruta_sospechosos}")

# Casos sin candidato
ruta_sin = os.path.join(OUT_DIR, "sin_candidato.csv")
sin_cand.to_csv(ruta_sin, index=False, encoding="utf-8")
print(f"\nCasos sin candidato: {len(sin_cand)}")
print(f"Guardados en: {ruta_sin}")
