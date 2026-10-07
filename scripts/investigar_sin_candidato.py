# ============================================================
# INVESTIGACION: CASOS SIN CANDIDATO
# Busca EL TOQUI y PLANTA EL PERAL en el catastro
# ============================================================

import pandas as pd
import os
import unicodedata

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"

# Cargar catastro
cat = pd.read_csv(os.path.join(DATA_DIR, "live_catastro.csv"))

def normalizar(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return texto

cat["FAENA_NORM"] = cat["NOMBRE_FAENA"].apply(normalizar)
cat["INSTALACION_NORM"] = cat["NOMBRE_INSTALACION"].apply(normalizar)

print("=" * 80)
print("INVESTIGACION DE CASOS SIN CANDIDATO")
print("=" * 80)

# ------------------------------------------------------------
# BUSQUEDA 1: EL TOQUI
# ------------------------------------------------------------
print("\n" + "=" * 80)
print("BUSQUEDA 1: EL TOQUI (comuna reportada: COYHAIQUE)")
print("=" * 80)

resultado = cat[
    cat["FAENA_NORM"].str.contains("TOQUI", na=False) |
    cat["INSTALACION_NORM"].str.contains("TOQUI", na=False)
]

print(f"\nRegistros encontrados en el catastro: {len(resultado)}")
if len(resultado) > 0:
    for i, row in resultado.iterrows():
        print(f"\n  ID: {row['ID']}")
        print(f"  Faena: {row['NOMBRE_FAENA']}")
        print(f"  Instalacion: {row['NOMBRE_INSTALACION']}")
        print(f"  Comuna: {row['COMUNA']}")
        print(f"  Region: {row['REGION']}")
        print(f"  UTM: N={row['UTM_NORTE']:.0f}, E={row['UTM_ESTE']:.0f}")
        print(f"  Tonelaje autorizado: {row['TONELAJE_AUTORIZADO']}")
else:
    print("  No se encontro ningun registro con 'TOQUI'")

# ------------------------------------------------------------
# BUSQUEDA 2: PLANTA EL PERAL
# ------------------------------------------------------------
print("\n" + "=" * 80)
print("BUSQUEDA 2: PLANTA EL PERAL (comuna reportada: EL TABO)")
print("=" * 80)

resultado2 = cat[
    cat["FAENA_NORM"].str.contains("PERAL", na=False) |
    cat["INSTALACION_NORM"].str.contains("PERAL", na=False)
]

print(f"\nRegistros encontrados en el catastro: {len(resultado2)}")
if len(resultado2) > 0:
    for i, row in resultado2.iterrows():
        print(f"\n  ID: {row['ID']}")
        print(f"  Faena: {row['NOMBRE_FAENA']}")
        print(f"  Instalacion: {row['NOMBRE_INSTALACION']}")
        print(f"  Comuna: {row['COMUNA']}")
        print(f"  Region: {row['REGION']}")
        print(f"  UTM: N={row['UTM_NORTE']:.0f}, E={row['UTM_ESTE']:.0f}")
        print(f"  Tonelaje autorizado: {row['TONELAJE_AUTORIZADO']}")
else:
    print("  No se encontro ningun registro con 'PERAL'")

# ------------------------------------------------------------
# BUSQUEDA 3: Región Aysén (para EL TOQUI)
# ------------------------------------------------------------
print("\n" + "=" * 80)
print("BUSQUEDA 3: Depositos en la region AYSEN (contexto)")
print("=" * 80)

aysen = cat[cat["REGION"].str.contains("Ays", case=False, na=False)]
print(f"\nDepositos en Aysen: {len(aysen)}")
for i, row in aysen.iterrows():
    print(f"  {row['ID']} | {row['NOMBRE_FAENA']} | {row['COMUNA']}")

# ------------------------------------------------------------
# BUSQUEDA 4: Depositos en la comuna El Tabo o cercanas
# ------------------------------------------------------------
print("\n" + "=" * 80)
print("BUSQUEDA 4: Depositos en El Tabo y comunas cercanas")
print("=" * 80)

comunas_cercanas = ["EL TABO", "CARTAGENA", "SAN ANTONIO", "SANTO DOMINGO"]
for comuna in comunas_cercanas:
    subset = cat[cat["COMUNA"].str.upper() == comuna]
    if len(subset) > 0:
        print(f"\nComuna {comuna}: {len(subset)} depositos")
        for i, row in subset.iterrows():
            print(f"  {row['ID']} | {row['NOMBRE_FAENA']} | {row['NOMBRE_INSTALACION']}")