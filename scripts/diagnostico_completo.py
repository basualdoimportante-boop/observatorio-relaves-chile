# ============================================================
# DIAGNOSTICO COMPLETO DE LOS TRES ARCHIVOS
# Muestra TODA la informacion disponible antes de decidir estrategia
# ============================================================

import pandas as pd
import os

DATA_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"

archivos = {
    "GEOQUIMICA": "live_geoquimica.csv",
    "OTRAS_MEDICIONES": "live_otras_mediciones.csv",
    "CATASTRO": "live_catastro.csv",
}

for nombre, archivo in archivos.items():
    ruta = os.path.join(DATA_DIR, archivo)
    df = pd.read_csv(ruta)
    
    print("=" * 80)
    print(f"ARCHIVO: {nombre}")
    print(f"Ruta: {archivo}")
    print("=" * 80)
    
    print(f"\nDimensiones: {df.shape[0]} filas x {df.shape[1]} columnas\n")
    
    # Tabla completa de columnas con tipo de dato y valores no nulos
    print(f"{'#':<4} {'COLUMNA':<35} {'TIPO':<12} {'NO-NULOS':<12} {'EJEMPLO':<40}")
    print("-" * 105)
    
    for i, col in enumerate(df.columns, 1):
        tipo = str(df[col].dtype)
        no_nulos = df[col].notna().sum()
        # Tomar un ejemplo no nulo
        ejemplo = df[col].dropna().iloc[0] if df[col].notna().any() else "VACIO"
        ejemplo_str = str(ejemplo)[:37]
        print(f"{i:<4} {col:<35} {tipo:<12} {no_nulos:<12} {ejemplo_str:<40}")
    
    print("\n")