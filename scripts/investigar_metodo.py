# ============================================================
# INVESTIGAR COLUMNA METODO CONSTRUCTIVO
# ============================================================

import pandas as pd
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

df = pd.read_csv(os.path.join(OUT_DIR, "ranking_con_exposicion.csv"))

print("=" * 70)
print("INVESTIGACION: METODO CONSTRUCTIVO")
print("=" * 70)

print(f"\nTotal depositos: {len(df)}")

# 1. Valores unicos y su frecuencia
print("\n--- Valores unicos de METODO_CONSTRUCTIVO_MURO ---")
conteo = df["METODO_CONSTRUCTIVO_MURO"].value_counts(dropna=False)
for valor, cantidad in conteo.items():
    print(f"  {str(valor):<30}: {cantidad}")

# 2. Cruce con estado
print("\n--- Cruce: METODO x ESTADO ---")
cruce = pd.crosstab(
    df["METODO_CONSTRUCTIVO_MURO"].fillna("(vacio)"),
    df["cat_estado"].fillna("(vacio)"),
    margins=True
)
print(cruce.to_string())

# 3. Cruce con exposicion a poblados
print("\n--- Cruce: METODO x EXPOSICION ---")
cruce2 = pd.crosstab(
    df["METODO_CONSTRUCTIVO_MURO"].fillna("(vacio)"),
    df["exposicion_poblados"],
    margins=True
)
print(cruce2.to_string())

# 4. Depositos sin metodo (datos faltantes)
print("\n--- Depositos SIN metodo constructivo registrado ---")
sin_metodo = df[df["METODO_CONSTRUCTIVO_MURO"].isna()]
print(f"  Total: {len(sin_metodo)}")
if len(sin_metodo) > 0:
    print(sin_metodo[["cat_id", "cat_nombre_faena", "cat_estado", "exposicion_poblados"]].head(20).to_string(index=False))