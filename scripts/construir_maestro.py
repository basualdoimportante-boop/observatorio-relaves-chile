# ============================================================
# CONSTRUIR ARCHIVO MAESTRO DE RELAVES
# Une geoquimica + catastro con estadisticas agregadas
# ============================================================

import pandas as pd
import numpy as np
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# ------------------------------------------------------------
# 1. CARGAR DATOS
# ------------------------------------------------------------
print("=" * 70)
print("CONSTRUYENDO ARCHIVO MAESTRO")
print("=" * 70)

print("\nCargando archivos...")
geoq = pd.read_csv(os.path.join(DATA_DIR, "live_geoquimica.csv"))
cat = pd.read_csv(os.path.join(DATA_DIR, "live_catastro.csv"))
cruce = pd.read_csv(os.path.join(OUT_DIR, "cruce_final_v3.csv"))

print(f"  Geoquimica: {len(geoq)} muestras")
print(f"  Catastro: {len(cat)} depositos")
print(f"  Cruce: {len(cruce)} asignaciones")

# ------------------------------------------------------------
# 2. IDENTIFICAR COLUMNAS DE ELEMENTOS QUIMICOS
# ------------------------------------------------------------
# Son todas las que empiezan con CON_ o POR_ (excepto POR_SUMA que es derivada)
elementos = [c for c in geoq.columns if (c.startswith("CON_") or c.startswith("POR_")) 
             and c not in ["POR_SUMA"]]

print(f"\nElementos a agregar: {len(elementos)}")

# ------------------------------------------------------------
# 3. UNIR CRUCE CON GEOQUIMICA
# ------------------------------------------------------------
print("\nUniendo cruce con geoquimica...")
muestras = cruce.merge(
    geoq[["ID"] + elementos],
    left_on="geoq_id",
    right_on="ID",
    how="left"
)

print(f"  Muestras unidas: {len(muestras)}")

# ------------------------------------------------------------
# 4. CREAR COLUMNA DE CONFIABILIDAD
# ------------------------------------------------------------
def categoria_a_confiabilidad(cat):
    if cat == "MATCH_AUTOMATICO":
        return "alta"
    elif cat in ["MATCH_ACEPTABLE", "MATCH_PROBABLE"]:
        return "media"
    elif cat == "MATCH_DUDOSO":
        return "baja"
    else:
        return "descartada"

muestras["confiabilidad"] = muestras["categoria"].apply(categoria_a_confiabilidad)

# Filtrar solo las usables (no descartadas)
muestras_usables = muestras[muestras["confiabilidad"] != "descartada"].copy()
print(f"  Muestras usables: {len(muestras_usables)}")

# ------------------------------------------------------------
# 5. AGREGAR POR DEPOSITO
# ------------------------------------------------------------
print("\nAgregando por deposito (esto puede tardar un poco)...")

# Eliminar muestras sin cat_id (sin match)
muestras_ok = muestras_usables[muestras_usables["cat_id"].notna()].copy()

# Diccionario para guardar los resultados
resultados = []

# Agrupar por deposito
for cat_id, grupo in muestras_ok.groupby("cat_id"):
    # Informacion basica del deposito
    fila = {
        "cat_id": cat_id,
        "cat_nombre_faena": grupo["cat_nombre_faena"].iloc[0],
        "cat_nombre_instalacion": grupo["cat_nombre_instalacion"].iloc[0],
        "cat_nombre_empresa": grupo["cat_nombre_empresa"].iloc[0],
        "cat_estado": grupo["cat_estado"].iloc[0],
        "cat_tonelaje_autorizado": grupo["cat_tonelaje_autorizado"].iloc[0],
        "n_muestras": len(grupo),
        "distancia_media_m": grupo["distancia_m"].mean(),
        "distancia_max_m": grupo["distancia_m"].max(),
    }
    
    # Confiabilidad general: la peor del grupo
    if "baja" in grupo["confiabilidad"].values:
        fila["confiabilidad"] = "baja"
    elif "media" in grupo["confiabilidad"].values:
        fila["confiabilidad"] = "media"
    else:
        fila["confiabilidad"] = "alta"
    
    # Categorias presentes
    fila["categorias_presentes"] = ",".join(sorted(grupo["categoria"].unique()))
    
    # Para cada elemento, calcular estadisticas
    for elem in elementos:
        valores = grupo[elem].dropna()
        if len(valores) > 0:
            fila[f"{elem}_prom"] = valores.mean()
            fila[f"{elem}_med"] = valores.median()
            fila[f"{elem}_max"] = valores.max()
            fila[f"{elem}_min"] = valores.min()
            fila[f"{elem}_n"] = len(valores)
        else:
            fila[f"{elem}_prom"] = np.nan
            fila[f"{elem}_med"] = np.nan
            fila[f"{elem}_max"] = np.nan
            fila[f"{elem}_min"] = np.nan
            fila[f"{elem}_n"] = 0
    
    resultados.append(fila)

df_maestro = pd.DataFrame(resultados)

# ------------------------------------------------------------
# 6. UNIR CON CATASTRO PARA AGREGAR COLUMNAS QUE FALTAN
# ------------------------------------------------------------
print("\nAgregando columnas del catastro...")

# Columnas del catastro que queremos
cols_cat = [
    "ID", "NOMBRE_FAENA", "NOMBRE_INSTALACION", "NOMBRE_EMPRESA_O_PRODUCTOR_MINE",
    "REGION", "PROVINCIA", "COMUNA", "LATITUD", "LONGITUD",
    "ESTADO_INSTALACION", "METODO_CONSTRUCTIVO_MURO",
    "TIPO_DEPOSITO", "RECURSO", "TIPO_MINERIA",
    "TONELAJE_AUTORIZADO", "VOL_AUTORIZADO", "CANTIDAD_MUROS__CONTENCION_",
]

cat_subset = cat[cols_cat].rename(columns={"ID": "cat_id"})

df_maestro = df_maestro.merge(cat_subset, on="cat_id", how="left")

# ------------------------------------------------------------
# 7. REPORTE FINAL
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("ARCHIVO MAESTRO CONSTRUIDO")
print("=" * 70)

print(f"\nDimensiones: {df_maestro.shape[0]} depositos x {df_maestro.shape[1]} columnas")

print(f"\nDistribucion por confiabilidad:")
for conf, cant in df_maestro["confiabilidad"].value_counts().items():
    pct = 100 * cant / len(df_maestro)
    print(f"  {conf}: {cant} ({pct:.1f}%)")

print(f"\nDepositos con al menos 1 muestra: {len(df_maestro)}")
print(f"Depositos con >= 3 muestras: {(df_maestro['n_muestras'] >= 3).sum()}")
print(f"Depositos con >= 5 muestras: {(df_maestro['n_muestras'] >= 5).sum()}")

print(f"\nTonelaje total cubierto: {df_maestro['cat_tonelaje_autorizado'].sum()/1e6:.1f} millones de toneladas")

# ------------------------------------------------------------
# 8. GUARDAR
# ------------------------------------------------------------
ruta_maestro = os.path.join(OUT_DIR, "maestro_relaves.csv")
df_maestro.to_csv(ruta_maestro, index=False, encoding="utf-8")
print(f"\nArchivo maestro guardado en: {ruta_maestro}")