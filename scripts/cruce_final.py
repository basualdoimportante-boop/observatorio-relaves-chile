# ============================================================
# CRUCE FINAL: GEOQUIMICA vs CATASTRO (con correcciones)
# - Equivalencia COIHAIQUE = COYHAIQUE
# - Marcado de casos descartados y dudosos
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

RADIO_TOLERANCIA = 500


def normalizar_texto(texto):
    """Convierte a mayusculas, quita tildes y aplica equivalencias."""
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    # Equivalencias ortograficas de comunas
    equivalencias = {
        "COIHAIQUE": "COYHAIQUE",
        "ALTO HOSPICIO": "ALTO HOSPICIO",  # placeholder
        "CALERA": "LA CALERA",
        "CALERA ": "LA CALERA",
    }
    return equivalencias.get(texto, texto)


# ------------------------------------------------------------
# 1. CARGAR DATOS
# ------------------------------------------------------------
print("=" * 70)
print("CRUCE FINAL: GEOQUIMICA vs CATASTRO")
print("=" * 70)

geoq = pd.read_csv(os.path.join(DATA_DIR, "live_geoquimica.csv"))
cat = pd.read_csv(os.path.join(DATA_DIR, "live_catastro.csv"))

print(f"\nGeoquimica: {len(geoq)} muestras")
print(f"Catastro: {len(cat)} depositos")

# Normalizar comunas
geoq["COMUNA_NORM"] = geoq["COMUNA"].apply(normalizar_texto)
cat["COMUNA_NORM"] = cat["COMUNA"].apply(normalizar_texto)

# ------------------------------------------------------------
# 2. CRUCE
# ------------------------------------------------------------
print("\n--- Procesando muestras ---")

resultados = []

for i, (idx, muestra) in enumerate(geoq.iterrows(), 1):
    if i % 500 == 0:
        print(f"  Procesadas {i}/{len(geoq)}...")
    
    comuna = muestra["COMUNA_NORM"]
    utm_n = muestra["UTM_NORTE"]
    utm_e = muestra["UTM_ESTE"]
    
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

df = pd.DataFrame(resultados)

# ------------------------------------------------------------
# 3. APLICAR CORRECCIONES MANUALES
# ------------------------------------------------------------
print("\n--- Aplicando correcciones manuales ---")

# 3.1 Descartar PUERTO CRISTAL (coordenadas invalidas)
mask_pc = (
    (df["geoq_nombre_fae"].str.upper() == "PUERTO CRISTAL") &
    (df["distancia_m"] > 100000)
)
df.loc[mask_pc, "categoria"] = "DESCARTADO_COORDENADAS_INVALIDAS"
print(f"  PUERTO CRISTAL marcados como descartados: {mask_pc.sum()}")

# 3.2 Descartar PLANTA EL PERAL (no existe en catastro)
mask_peral = df["geoq_nombre_fae"].str.upper().str.contains("PERAL", na=False)
df.loc[mask_peral, "categoria"] = "DESCARTADO_NO_EN_CATASTRO"
print(f"  PLANTA EL PERAL marcados como descartados: {mask_peral.sum()}")

# 3.3 Marcar DAIRE y SALVADOR como dudosos
mask_daire = df["geoq_nombre_fae"].str.upper() == "DAIRE"
mask_salvador = df["geoq_nombre_fae"].str.upper() == "SALVADOR"
df.loc[mask_daire, "categoria"] = "MATCH_DUDOSO"
df.loc[mask_salvador, "categoria"] = "MATCH_DUDOSO"
print(f"  DAIRE marcados como dudosos: {mask_daire.sum()}")
print(f"  SALVADOR marcados como dudosos: {mask_salvador.sum()}")

# ------------------------------------------------------------
# 4. REPORTE FINAL
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("RESULTADOS DEL CRUCE FINAL")
print("=" * 70)

conteo = df["categoria"].value_counts()
print("\nCategorias:")
for cat_nombre, cantidad in conteo.items():
    porcentaje = 100 * cantidad / len(df)
    print(f"  {cat_nombre}: {cantidad} ({porcentaje:.1f}%)")

# Depositos unicos
depositos_asignados = df[df["cat_id"].notna()]["cat_id"].nunique()
print(f"\nDepositos unicos del catastro con al menos 1 muestra: {depositos_asignados}")

# ------------------------------------------------------------
# 5. GUARDAR
# ------------------------------------------------------------
ruta_final = os.path.join(OUT_DIR, "cruce_final.csv")
df.to_csv(ruta_final, index=False, encoding="utf-8")
print(f"\nResultados guardados en: {ruta_final}")

# Guardar solo los usables (excluyendo descartados)
df_usables = df[~df["categoria"].str.startswith("DESCARTADO")]
ruta_usables = os.path.join(OUT_DIR, "cruce_usables.csv")
df_usables.to_csv(ruta_usables, index=False, encoding="utf-8")
print(f"Cruce usable (sin descartados): {ruta_usables}")
print(f"  Muestras usables: {len(df_usables)}")