# ============================================================
# COMPARACION DE CAMPOS: GEOQUIMICA vs CATASTRO
# Para los casos en REVISION_MANUAL y SOSPECHOSO_MAYOR_10KM
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


# 1. Cargar archivos
geoq = pd.read_csv(os.path.join(DATA_DIR, "live_geoquimica.csv"))
cat = pd.read_csv(os.path.join(DATA_DIR, "live_catastro.csv"))
cruce = pd.read_csv(os.path.join(OUT_DIR, "cruce_final_v2.csv"))

# 2. Filtrar solo los casos problematicos
casos = cruce[cruce["categoria"].isin(["REVISION_MANUAL", "SOSPECHOSO_MAYOR_10KM"])].copy()
print(f"Total casos a investigar: {len(casos)}")

# 3. Unir con geoquimica (para recuperar los nombres originales)
casos = casos.merge(
    geoq[["ID", "NOMBRE_EMP", "NOMBRE_FAE", "NOMBRE_INS", "RECURSO", "REGION", "COMUNA", "ESTADO_INS"]],
    left_on="geoq_id",
    right_on="ID",
    how="left",
    suffixes=("", "_geoq")
)

# 4. Unir con catastro (para recuperar los nombres del catastro)
casos = casos.merge(
    cat[["ID", "NOMBRE_EMPRESA_O_PRODUCTOR_MINE", "NOMBRE_FAENA", "NOMBRE_INSTALACION",
         "RECURSO", "REGION", "COMUNA", "ESTADO_INSTALACION"]],
    left_on="cat_id",
    right_on="ID",
    how="left",
    suffixes=("_geoq", "_cat")
)

# 5. Calcular coincidencias columna por columna
def coincide(a, b):
    return normalizar(a) == normalizar(b)

casos["coincide_empresa"] = casos.apply(
    lambda r: coincide(r.get("NOMBRE_EMP_geoq", r.get("NOMBRE_EMP")),
                       r.get("NOMBRE_EMPRESA_O_PRODUCTOR_MINE")), axis=1)

casos["coincide_faena"] = casos.apply(
    lambda r: coincide(r.get("NOMBRE_FAE_geoq", r.get("NOMBRE_FAE")),
                       r.get("NOMBRE_FAENA")), axis=1)

casos["coincide_instalacion"] = casos.apply(
    lambda r: coincide(r.get("NOMBRE_INS_geoq", r.get("NOMBRE_INS")),
                       r.get("NOMBRE_INSTALACION")), axis=1)

casos["coincide_region"] = casos.apply(
    lambda r: coincide(r.get("REGION_geoq", r.get("REGION")),
                       r.get("REGION_cat")), axis=1)

casos["coincide_comuna"] = casos.apply(
    lambda r: coincide(r.get("COMUNA_geoq", r.get("COMUNA")),
                       r.get("COMUNA_cat")), axis=1)

# 6. Mostrar resultados
print("\n" + "=" * 90)
print("COINCIDENCIAS POR CAMPO")
print("=" * 90)

for col in ["coincide_empresa", "coincide_faena", "coincide_instalacion", "coincide_region", "coincide_comuna"]:
    n = casos[col].sum()
    pct = 100 * n / len(casos)
    print(f"  {col:<25}: {n:>4} ({pct:.1f}%)")

# 7. Distribucion combinada
print("\n" + "=" * 90)
print("CUANTAS COLUMNAS COINCIDEN POR CASO")
print("=" * 90)

casos["n_coincidencias"] = casos[[
    "coincide_empresa", "coincide_faena", "coincide_instalacion",
    "coincide_region", "coincide_comuna"
]].sum(axis=1)

dist = casos["n_coincidencias"].value_counts().sort_index(ascending=False)
for n, cantidad in dist.items():
    print(f"  {n} columnas coinciden: {cantidad} casos")

# 8. Guardar tabla completa
ruta = os.path.join(OUT_DIR, "comparacion_campos.csv")
casos.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nTabla completa guardada en: {ruta}")

# 9. Mostrar los primeros 15 casos con detalle
print("\n" + "=" * 90)
print("DETALLE DE LOS PRIMEROS 15 CASOS")
print("=" * 90)

for i, row in casos.head(15).iterrows():
    print(f"\n--- Caso {i} (geoq_id={row['geoq_id']}, cat_id={row['cat_id']}, dist={row['distancia_m']:.0f} m) ---")
    print(f"  Empresa   geoq: {row.get('NOMBRE_EMP_geoq', row.get('NOMBRE_EMP'))}")
    print(f"  Empresa   cat:  {row.get('NOMBRE_EMPRESA_O_PRODUCTOR_MINE')}  [{row['coincide_empresa']}]")
    print(f"  Faena     geoq: {row.get('NOMBRE_FAE_geoq', row.get('NOMBRE_FAE'))}")
    print(f"  Faena     cat:  {row.get('NOMBRE_FAENA')}  [{row['coincide_faena']}]")
    print(f"  Instalac. geoq: {row.get('NOMBRE_INS_geoq', row.get('NOMBRE_INS'))}")
    print(f"  Instalac. cat:  {row.get('NOMBRE_INSTALACION')}  [{row['coincide_instalacion']}]")