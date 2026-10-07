# ============================================================
# DIAGNOSTICO DE CRUCE: GEOQUIMICA vs CATASTRO
# Estrategia: misma comuna + distancia UTM <= 500 m
# Prueba con 100 muestras aleatorias
# ============================================================

import pandas as pd
import numpy as np
import os
import unicodedata

# ------------------------------------------------------------
# CONFIGURACION
# ------------------------------------------------------------
DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"
os.makedirs(OUT_DIR, exist_ok=True)

RADIO_TOLERANCIA = 500  # metros
N_MUESTRAS_PRUEBA = 100
SEMILLA = 42  # para reproducibilidad


def normalizar_texto(texto):
    """Convierte a mayusculas, quita tildes y espacios extra."""
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    # Quitar tildes
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return texto


# ------------------------------------------------------------
# 1. CARGAR DATOS
# ------------------------------------------------------------
print("=" * 70)
print("DIAGNOSTICO DE CRUCE GEOQUIMICA vs CATASTRO")
print("=" * 70)

print("\nCargando archivos...")
geoq = pd.read_csv(os.path.join(DATA_DIR, "live_geoquimica.csv"))
cat = pd.read_csv(os.path.join(DATA_DIR, "live_catastro.csv"))

print(f"  Geoquimica: {len(geoq)} muestras")
print(f"  Catastro: {len(cat)} depositos")

# ------------------------------------------------------------
# 2. VERIFICAR SISTEMA DE COORDENADAS
# ------------------------------------------------------------
print("\n--- Verificacion de coordenadas ---")
if "DATUM" in cat.columns:
    print(f"  Datum del catastro: {cat['DATUM'].unique()}")
if "HUSO" in cat.columns:
    print(f"  Huso del catastro: {cat['HUSO'].unique()}")

print(f"\n  UTM_NORTE catastro: min={cat['UTM_NORTE'].min():.0f}, max={cat['UTM_NORTE'].max():.0f}")
print(f"  UTM_ESTE catastro: min={cat['UTM_ESTE'].min():.0f}, max={cat['UTM_ESTE'].max():.0f}")
print(f"  UTM_NORTE geoquimica: min={geoq['UTM_NORTE'].min():.0f}, max={geoq['UTM_NORTE'].max():.0f}")
print(f"  UTM_ESTE geoquimica: min={geoq['UTM_ESTE'].min():.0f}, max={geoq['UTM_ESTE'].max():.0f}")

# ------------------------------------------------------------
# 3. NORMALIZAR COMUNAS
# ------------------------------------------------------------
print("\n--- Normalizando nombres de comunas ---")
geoq["COMUNA_NORM"] = geoq["COMUNA"].apply(normalizar_texto)
cat["COMUNA_NORM"] = cat["COMUNA"].apply(normalizar_texto)

print(f"  Comunas unicas en geoquimica: {geoq['COMUNA_NORM'].nunique()}")
print(f"  Comunas unicas en catastro: {cat['COMUNA_NORM'].nunique()}")

comunas_comunes = set(geoq["COMUNA_NORM"]) & set(cat["COMUNA_NORM"])
print(f"  Comunas comunes: {len(comunas_comunes)}")

# ------------------------------------------------------------
# 4. SELECCIONAR MUESTRA ALEATORIA
# ------------------------------------------------------------
print(f"\n--- Seleccionando {N_MUESTRAS_PRUEBA} muestras aleatorias ---")
muestras = geoq.sample(n=N_MUESTRAS_PRUEBA, random_state=SEMILLA).copy()
print(f"  Muestras seleccionadas: {len(muestras)}")

# ------------------------------------------------------------
# 5. CRUCE POR COMUNA + DISTANCIA
# ------------------------------------------------------------
print("\n--- Procesando cada muestra ---")

resultados = []

for idx, muestra in muestras.iterrows():
    comuna = muestra["COMUNA_NORM"]
    utm_n = muestra["UTM_NORTE"]
    utm_e = muestra["UTM_ESTE"]
    
    # Filtrar catastro por misma comuna
    candidatos = cat[cat["COMUNA_NORM"] == comuna].copy()
    
    if len(candidatos) == 0:
        resultados.append({
            "geoq_id": muestra["ID"],
            "geoq_nombre_fae": muestra["NOMBRE_FAE"],
            "geoq_comuna": muestra["COMUNA"],
            "geoq_utm_norte": utm_n,
            "geoq_utm_este": utm_e,
            "cat_id": None,
            "cat_nombre_faena": None,
            "cat_nombre_instalacion": None,
            "distancia_m": None,
            "categoria": "SIN_CANDIDATO",
        })
        continue
    
    # Calcular distancia a cada candidato
    candidatos["distancia"] = np.sqrt(
        (candidatos["UTM_NORTE"] - utm_n) ** 2 +
        (candidatos["UTM_ESTE"] - utm_e) ** 2
    )
    
    # Tomar el mas cercano
    mas_cercano = candidatos.loc[candidatos["distancia"].idxmin()]
    distancia = mas_cercano["distancia"]
    
    if distancia <= RADIO_TOLERANCIA:
        categoria = "MATCH_AUTOMATICO"
    else:
        categoria = "REVISION_MANUAL"
    
    resultados.append({
        "geoq_id": muestra["ID"],
        "geoq_nombre_fae": muestra["NOMBRE_FAE"],
        "geoq_comuna": muestra["COMUNA"],
        "geoq_utm_norte": utm_n,
        "geoq_utm_este": utm_e,
        "cat_id": mas_cercano["ID"],
        "cat_nombre_faena": mas_cercano["NOMBRE_FAENA"],
        "cat_nombre_instalacion": mas_cercano["NOMBRE_INSTALACION"],
        "distancia_m": round(distancia, 1),
        "categoria": categoria,
    })

df_resultados = pd.DataFrame(resultados)

# ------------------------------------------------------------
# 6. REPORTE
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("RESULTADOS DEL DIAGNOSTICO")
print("=" * 70)

conteo = df_resultados["categoria"].value_counts()
print("\nCategorias:")
for cat_nombre, cantidad in conteo.items():
    porcentaje = 100 * cantidad / len(df_resultados)
    print(f"  {cat_nombre}: {cantidad} ({porcentaje:.1f}%)")

# Estadisticas de distancia (solo donde hay match)
con_distancia = df_resultados[df_resultados["distancia_m"].notna()]
if len(con_distancia) > 0:
    print("\nEstadisticas de distancia (solo donde hay candidato):")
    print(f"  Minima: {con_distancia['distancia_m'].min():.1f} m")
    print(f"  Mediana: {con_distancia['distancia_m'].median():.1f} m")
    print(f"  Media: {con_distancia['distancia_m'].mean():.1f} m")
    print(f"  Maxima: {con_distancia['distancia_m'].max():.1f} m")
    print(f"  Percentil 25: {con_distancia['distancia_m'].quantile(0.25):.1f} m")
    print(f"  Percentil 75: {con_distancia['distancia_m'].quantile(0.75):.1f} m")
    print(f"  Percentil 90: {con_distancia['distancia_m'].quantile(0.90):.1f} m")

# Top 10 mas cercanos
print("\nTop 10 matches mas cercanos:")
top_cerca = df_resultados.nsmallest(10, "distancia_m")[
    ["geoq_id", "geoq_nombre_fae", "cat_id", "cat_nombre_faena", "distancia_m"]
]
print(top_cerca.to_string(index=False))

# Top 10 mas lejanos
print("\nTop 10 matches mas lejanos (candidatos a revision):")
top_lejos = df_resultados.nlargest(10, "distancia_m")[
    ["geoq_id", "geoq_nombre_fae", "cat_id", "cat_nombre_faena", "distancia_m"]
]
print(top_lejos.to_string(index=False))

# ------------------------------------------------------------
# 7. GUARDAR RESULTADOS
# ------------------------------------------------------------
ruta_salida = os.path.join(OUT_DIR, "diagnostico_cruce_100.csv")
df_resultados.to_csv(ruta_salida, index=False, encoding="utf-8")
print(f"\nResultados guardados en: {ruta_salida}")