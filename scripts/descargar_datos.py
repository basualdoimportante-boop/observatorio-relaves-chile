# ============================================================
# SCRIPT 03: DESCARGAR DATOS DE SERNAGEOMIN (SERVICIO EN VIVO)
# Basado en fetch_live.py del artículo científico
# ============================================================

import requests
import json
import os
import time
import pandas as pd

# 1. URLs correctas del servicio (del artículo)
ROOT = "https://services1.arcgis.com/OyjvVdFTl5hfSdX3/arcgis/rest/services"
BASE = f"{ROOT}/PLATAFORMA_PUBLICA_RELAVES_WFL1/FeatureServer"
CADASTRE = f"{ROOT}/CDR_CHILE_PUNTUAL_2025/FeatureServer/0"

# 2. Capas a descargar
#    25 = GQ_RELAVES (geoquímica de superficie, ~2131 registros)
#    3  = GQ_RELAVES_OM (mediciones subterráneas, ~478 registros)
LAYERS = {25: "geoquimica", 3: "otras_mediciones"}

# 3. Tamaño de página
PAGE = 1000

# 4. Carpeta de salida
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
os.makedirs(OUT_DIR, exist_ok=True)


def descargar_capa(endpoint, nombre):
    """Descarga todos los registros de una capa, paginando si es necesario."""
    features = []
    offset = 0

    while True:
        print(f"  Descargando {nombre} (offset={offset})...")
        response = requests.get(
            f"{endpoint}/query",
            params={
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
                "f": "json",
                "resultOffset": offset,
                "resultRecordCount": PAGE,
            },
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()

        if "error" in payload:
            raise SystemExit(f"Error del servicio: {payload['error']}")

        batch = payload.get("features", [])
        features += [f["attributes"] for f in batch]

        # Si el lote fue más pequeño que PAGE, ya no hay más
        if len(batch) < PAGE:
            break

        offset += len(batch)
        time.sleep(0.3)  # Cortesía con el servidor

    # Guardar como CSV
    df = pd.DataFrame(features)
    ruta = os.path.join(OUT_DIR, f"live_{nombre}.csv")
    df.to_csv(ruta, index=False, encoding="utf-8")
    print(f"  ✓ {nombre}: {len(features)} registros -> {ruta}")
    return df


def main():
    print("=" * 60)
    print("DESCARGA DE DATOS DE SERNAGEOMIN")
    print("=" * 60)

    # Descargar las 2 capas de geoquímica
    for layer_id, nombre in LAYERS.items():
        descargar_capa(f"{BASE}/{layer_id}", nombre)

    # Descargar el catastro
    descargar_capa(CADASTRE, "catastro")

    print("\nDescarga completada.")


if __name__ == "__main__":
    main()
    