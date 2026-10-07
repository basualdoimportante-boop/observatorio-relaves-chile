# ============================================================
# CRUCE COMPLETO: GEOQUIMICA vs CATASTRO
# Estrategia: misma comuna + distancia UTM <= 500 m
# Procesa las 2.131 muestras
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


def normalizar_texto(texto):
    """Convierte a mayusculas, quita tildes y espacios extra."""
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return texto


# ------------------------------------------------------------
# 1. CARGAR DATOS
# ------------------------------------------------------------
print("=" * 70)
print("CRUCE COMPLETO: GEOQUIMICA vs CATASTRO")
print("=" * 70)

print("\nCargando archivos...")
geoq = pd.read_csv(os.path.join(DATA_DIR, "live_geoquimica.csv"))
cat = pd.read_csv(os.path.join(DATA_DIR, "live_catastro.csv"))

print(f"  Geoquimica: {len(geoq)} muestras")
print(f"  Catastro: {len(cat)} depositos")

# Normalizar comunas
geoq["COMUNA_NORM"] = geoq["COMUNA"].apply(normalizar_texto)
cat["COMUNA_NORM"] = cat["COMUNA"].apply(normalizar_texto)

# ------------------------------------------------------------
# 2. CRUCE PARA TODAS LAS MUESTRAS
# ------------------------------------------------------------
print("\n--- Procesando todas las muestras ---")

resultados = []

for i, (idx, muestra) in enumerate(geoq.iterrows(), 1):
    if i % 500 == 0:
        print(f"  Procesadas {i}/{len(geoq)}...")
    
    comuna = muestra["COMUNA_NORM"]
    utm_n = muestra["UTM_NORTE"]
    utm_e = muestra["UTM_ESTE"]
    
    # Filtrar catastro por misma comuna
    candidatos = cat[cat["COMUNA_NORM"] == comuna]
    
    if len(candidatos) == 0:
        resultados.append({
            "geoq_id": muestra["ID"],
            "geoq_nombre_emp": muestra["NOMBRE_EMP"],
            "geoq_nombre_fae": muestra["NOMBRE_FAE"],
            "geoq_nombre_ins": muestra["NOMBRE_INS"],
            "geoq_comuna": muestra["COMUNA"],
            "geoq_utm_norte": utm_n,
            "geoq_utm_este": utm_e,
            "cat_id": None,
            "cat_nombre_empresa": None,
            "cat_nombre_faena": None,
            "cat_nombre_instalacion": None,
            "cat_estado": None,
            "cat_tonelaje_autorizado": None,
            "distancia_m": None,
            "categoria": "SIN_CANDIDATO",
        })
        continue
    
    # Calcular distancia a cada candidato
    distancias = np.sqrt(
        (candidatos["UTM_NORTE"] - utm_n) ** 2 +
        (candidatos["UTM_ESTE"] - utm_e) ** 2
    )
    
    idx_min = distancias.idxmin()
    mas_cercano = candidatos.loc[idx_min]
    distancia = distancias.loc[idx_min]
    
    if distancia <= RADIO_TOLERANCIA:
        categoria = "MATCH_AUTOMATICO"
    else:
        categoria = "REVISION_MANUAL"
    
    resultados.append({
        "geoq_id": muestra["ID"],
        "geoq_nombre_emp": muestra["NOMBRE_EMP"],
        "geoq_nombre_fae": muestra["NOMBRE_FAE"],
        "geoq_nombre_ins": muestra["NOMBRE_INS"],
        "geoq_comuna": muestra["COMUNA"],
        "geoq_utm_norte": utm_n,
        "geoq_utm_este": utm_e,
        "cat_id": mas_cercano["ID"],
        "cat_nombre_empresa": mas_cercano["NOMBRE_EMPRESA_O_PRODUCTOR_MINE"],
        "cat_nombre_faena": mas_cercano["NOMBRE_FAENA"],
        "cat_nombre_instalacion": mas_cercano["NOMBRE_INSTALACION"],
        "cat_estado": mas_cercano["ESTADO_INSTALACION"],
        "cat_tonelaje_autorizado": mas_cercano["TONELAJE_AUTORIZADO"],
        "distancia_m": round(distancia, 1),
        "categoria": categoria,
    })

df_resultados = pd.DataFrame(resultados)

# ------------------------------------------------------------
# 3. REPORTE
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("RESULTADOS DEL CRUCE COMPLETO")
print("=" * 70)

conteo = df_resultados["categoria"].value_counts()
print("\nCategorias:")
for cat_nombre, cantidad in conteo.items():
    porcentaje = 100 * cantidad / len(df_resultados)
    print(f"  {cat_nombre}: {cantidad} ({porcentaje:.1f}%)")

con_distancia = df_resultados[df_resultados["distancia_m"].notna()]
if len(con_distancia) > 0:
    print("\nEstadisticas de distancia:")
    print(f"  Minima: {con_distancia['distancia_m'].min():.1f} m")
    print(f"  Mediana: {con_distancia['distancia_m'].median():.1f} m")
    print(f"  Media: {con_distancia['distancia_m'].mean():.1f} m")
    print(f"  Maxima: {con_distancia['distancia_m'].max():.1f} m")
    print(f"  Percentil 90: {con_distancia['distancia_m'].quantile(0.90):.1f} m")
    print(f"  Percentil 95: {con_distancia['distancia_m'].quantile(0.95):.1f} m")

# Cuantos depositos unicos del catastro fueron asignados
depositos_asignados = df_resultados["cat_id"].nunique()
print(f"\nDepositos unicos del catastro con al menos 1 muestra asignada: {depositos_asignados}")

# ------------------------------------------------------------
# 4. GUARDAR RESULTADOS
# ------------------------------------------------------------
ruta_completa = os.path.join(OUT_DIR, "cruce_completo.csv")
df_resultados.to_csv(ruta_completa, index=False, encoding="utf-8")
print(f"\nResultados completos guardados en: {ruta_completa}")

# Guardar solo los casos de revision manual
revision = df_resultados[df_resultados["categoria"] == "REVISION_MANUAL"]
if len(revision) > 0:
    ruta_revision = os.path.join(OUT_DIR, "revision_manual.csv")
    revision.to_csv(ruta_revision, index=False, encoding="utf-8")
    print(f"Casos para revision manual guardados en: {ruta_revision}")