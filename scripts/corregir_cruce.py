# ============================================================
# CORRECCION FINAL DEL CRUCE
# Revierte la sobre-correccion de SALVADOR y DAIRE
# ============================================================

import pandas as pd
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# Cargar el cruce final
df = pd.read_csv(os.path.join(OUT_DIR, "cruce_final.csv"))

print("=" * 70)
print("CORRECCION DEL CRUCE")
print("=" * 70)

# 1. Revertir MATCH_DUDOSO a su clasificacion original por distancia
#    Excepto para los casos con distancia > 10 km que quedan como sospechosos
mask_dudoso = df["categoria"] == "MATCH_DUDOSO"

# Los que tienen distancia <= 500 m vuelven a MATCH_AUTOMATICO
df.loc[mask_dudoso & (df["distancia_m"] <= 500), "categoria"] = "MATCH_AUTOMATICO"

# Los que tienen distancia entre 500 m y 10 km vuelven a REVISION_MANUAL
df.loc[mask_dudoso & (df["distancia_m"] > 500) & (df["distancia_m"] <= 10000), "categoria"] = "REVISION_MANUAL"

# Los que tienen distancia > 10 km se marcan como SOSPECHOSO
df.loc[mask_dudoso & (df["distancia_m"] > 10000), "categoria"] = "SOSPECHOSO_MAYOR_10KM"

# 2. Reporte final
print("\n--- Correcciones aplicadas ---")
print(f"  Muestras que eran MATCH_DUDOSO: {mask_dudoso.sum()}")
print(f"  Reclasificadas a MATCH_AUTOMATICO: {(mask_dudoso & (df['distancia_m'] <= 500)).sum()}")
print(f"  Reclasificadas a REVISION_MANUAL: {(mask_dudoso & (df['distancia_m'] > 500) & (df['distancia_m'] <= 10000)).sum()}")
print(f"  Reclasificadas a SOSPECHOSO_MAYOR_10KM: {(mask_dudoso & (df['distancia_m'] > 10000)).sum()}")

print("\n" + "=" * 70)
print("DISTRIBUCION FINAL")
print("=" * 70)

conteo = df["categoria"].value_counts()
for cat, cantidad in conteo.items():
    pct = 100 * cantidad / len(df)
    print(f"  {cat}: {cantidad} ({pct:.1f}%)")

# 3. Guardar el archivo corregido
ruta_corregido = os.path.join(OUT_DIR, "cruce_final_v2.csv")
df.to_csv(ruta_corregido, index=False, encoding="utf-8")
print(f"\nArchivo corregido guardado en: {ruta_corregido}")

# 4. Guardar solo usables (sin los descartados)
df_usables = df[~df["categoria"].str.startswith("DESCARTADO") & (df["categoria"] != "SOSPECHOSO_MAYOR_10KM")]
ruta_usables = os.path.join(OUT_DIR, "cruce_usables_v2.csv")
df_usables.to_csv(ruta_usables, index=False, encoding="utf-8")
print(f"Cruce usable guardado en: {ruta_usables}")
print(f"  Muestras usables: {len(df_usables)}")

# 5. Verificar SALVADOR especificamente
print("\n" + "=" * 70)
print("VERIFICACION: MUESTRAS SALVADOR")
print("=" * 70)
salvador = df[df["geoq_nombre_fae"].str.upper() == "SALVADOR"]
print(salvador["categoria"].value_counts().to_string())