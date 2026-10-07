# ============================================================
# DESCARGA COMPLETA DE DATOS DE SERNAGEOMIN
# Usa urllib (nativo de Python, sin dependencias externas)
# ============================================================

import urllib.request
import urllib.parse
import json
import csv
import os
import time

# 1. URLs de los servicios
ROOT = "https://services1.arcgis.com/OyjvVdFTl5hfSdX3/arcgis/rest/services"
BASE = f"{ROOT}/PLATAFORMA_PUBLICA_RELAVES_WFL1/FeatureServer"
CADASTRE = f"{ROOT}/CDR_CHILE_PUNTUAL_2025/FeatureServer/0"

# 2. Capas a descargar
LAYERS = {
    25: "geoquimica",
    3: "otras_mediciones",
}
CADASTRE_NAME = "catastro"

# 3. Configuracion
PAGE = 1000
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
os.makedirs(OUT_DIR, exist_ok=True)


def descargar_capa(endpoint, nombre):
    """Descarga todos los registros de una capa con paginacion."""
    print(f"\n--- Descargando: {nombre} ---")
    
    todos = []
    offset = 0
    
    while True:
        params = urllib.parse.urlencode({
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": PAGE,
        })
        url = f"{endpoint}/query?{params}"
        
        print(f"  Descargando desde offset={offset}...")
        
        try:
            with urllib.request.urlopen(url, timeout=120) as response:
                datos = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"  Error en la descarga: {e}")
            break
        
        if "error" in datos:
            print(f"  Error del servicio: {datos['error']}")
            break
        
        batch = datos.get("features", [])
        todos.extend([f["attributes"] for f in batch])
        
        print(f"  Recibidos: {len(batch)} registros (total: {len(todos)})")
        
        if len(batch) < PAGE:
            break
        
        offset += len(batch)
        time.sleep(0.5)
    
    # Guardar como CSV
    if todos:
        ruta = os.path.join(OUT_DIR, f"live_{nombre}.csv")
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=todos[0].keys())
            writer.writeheader()
            writer.writerows(todos)
        print(f"  Guardado: {ruta} ({len(todos)} registros)")
    else:
        print(f"  No se descargaron datos de {nombre}")


def main():
    print("=" * 60)
    print("DESCARGA DE DATOS DE SERNAGEOMIN")
    print("=" * 60)
    
    # Descargar capas de geoquimica
    for layer_id, nombre in LAYERS.items():
        descargar_capa(f"{BASE}/{layer_id}", nombre)
    
    # Descargar catastro
    descargar_capa(CADASTRE, CADASTRE_NAME)
    
    print("\n" + "=" * 60)
    print("DESCARGA COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    main()