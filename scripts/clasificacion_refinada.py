# ============================================================
# CLASIFICACION REFINADA DEL CRUCE
# Aplica reglas basadas en coincidencias de texto
# ============================================================

import pandas as pd
import os
import unicodedata

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"


def normalizar(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return texto


def coincide(a, b):
    """Compara dos textos de forma flexible."""
    a_norm = normalizar(a)
    b_norm = normalizar(b)
    if not a_norm or not b_norm:
        return False
    if a_norm == b_norm:
        return True
    # Verificar si uno contiene al otro (para abreviaturas)
    if len(a_norm) > 3 and len(b_norm) > 3:
        if a_norm in b_norm or b_norm in a_norm:
            return True
    return False


# 1. Cargar
geoq = pd.read_csv(os.path.join(DATA_DIR, "live_geoquimica.csv"))
cat = pd.read_csv(os.path.join(DATA_DIR, "live_catastro.csv"))
cruce = pd.read_csv(os.path.join(OUT_DIR, "cruce_final_v2.csv"))

# 2. Unir con geoquimica y catastro
casos = cruce.merge(
    geoq[["ID", "NOMBRE_EMP", "NOMBRE_FAE", "NOMBRE_INS", "REGION", "COMUNA"]],
    left_on="geoq_id", right_on="ID", how="left"
).merge(
    cat[["ID", "NOMBRE_EMPRESA_O_PRODUCTOR_MINE", "NOMBRE_FAENA",
         "NOMBRE_INSTALACION", "REGION", "COMUNA"]],
    left_on="cat_id", right_on="ID", how="left",
    suffixes=("_geoq", "_cat")
)

# 3. Calcular coincidencias
casos["coincide_empresa"] = casos.apply(
    lambda r: coincide(r["NOMBRE_EMP"], r["NOMBRE_EMPRESA_O_PRODUCTOR_MINE"]), axis=1)
casos["coincide_faena"] = casos.apply(
    lambda r: coincide(r["NOMBRE_FAE"], r["NOMBRE_FAENA"]), axis=1)
casos["coincide_instalacion"] = casos.apply(
    lambda r: coincide(r["NOMBRE_INS"], r["NOMBRE_INSTALACION"]), axis=1)
casos["coincide_region"] = casos.apply(
    lambda r: coincide(r["REGION_geoq"], r["REGION_cat"]), axis=1)
casos["coincide_comuna"] = casos.apply(
    lambda r: coincide(r["COMUNA_geoq"], r["COMUNA_cat"]), axis=1)

casos["n_coincidencias"] = casos[[
    "coincide_empresa", "coincide_faena", "coincide_instalacion",
    "coincide_region", "coincide_comuna"
]].sum(axis=1)

# 4. Reclasificar solo los casos en REVISION_MANUAL o SOSPECHOSO
mask_revisar = casos["categoria"].isin(["REVISION_MANUAL", "SOSPECHOSO_MAYOR_10KM"])

# Aplicar reglas
casos.loc[mask_revisar & (casos["n_coincidencias"] >= 4), "categoria"] = "MATCH_ACEPTABLE"
casos.loc[mask_revisar & (casos["n_coincidencias"] == 3), "categoria"] = "MATCH_PROBABLE"
casos.loc[mask_revisar & (casos["n_coincidencias"] == 2), "categoria"] = "MATCH_DUDOSO"
casos.loc[mask_revisar & (casos["n_coincidencias"] <= 1), "categoria"] = "DESCARTADO_MISMATCH"

# 5. Reporte
print("=" * 70)
print("CLASIFICACION REFINADA")
print("=" * 70)

conteo = casos["categoria"].value_counts()
print("\nDistribucion final:")
for cat_nombre, cantidad in conteo.items():
    pct = 100 * cantidad / len(casos)
    print(f"  {cat_nombre}: {cantidad} ({pct:.1f}%)")

# 6. Muestras usables
usables = casos[~casos["categoria"].str.startswith("DESCARTADO")]
print(f"\nMuestras usables: {len(usables)} ({100*len(usables)/len(casos):.1f}%)")

# 7. Guardar
ruta_final = os.path.join(OUT_DIR, "cruce_final_v3.csv")
casos.to_csv(ruta_final, index=False, encoding="utf-8")
print(f"\nGuardado en: {ruta_final}")

ruta_usables = os.path.join(OUT_DIR, "cruce_usables_v3.csv")
usables.to_csv(ruta_usables, index=False, encoding="utf-8")
print(f"Cruce usable: {ruta_usables}")