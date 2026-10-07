# Verificar cuantas muestras de SALVADOR estan en cada categoria
import pandas as pd
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"
df = pd.read_csv(os.path.join(OUT_DIR, "cruce_final.csv"))

salvador = df[df["geoq_nombre_fae"].str.upper() == "SALVADOR"]
print(f"Total muestras SALVADOR: {len(salvador)}")
print(f"\nDistribucion por categoria:")
print(salvador["categoria"].value_counts())

print(f"\nDistancias de las muestras SALVADOR:")
print(salvador[["geoq_id", "cat_id", "cat_nombre_faena", "distancia_m", "categoria"]].to_string(index=False))