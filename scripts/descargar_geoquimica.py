# ============================================================
# DESCARGA SOLO DE LA CAPA GEOQUIMICA (con reintentos)
# ============================================================

import urllib.request
import urllib.parse
import json
import csv
import os
import time

# Configuracion
BASE = "https://services1.arcgis.com/OyjvVdFTl5hfSdX3/arcgis/rest/services/PLATAFORMA_PUBLICA_RELAVES_WFL1/FeatureServer"
LAYER_ID = 25  # GQ_RELAVES
NOMBRE = "geoquimica"
PAGE = 500  # Lotes mas pequeños para evitar timeout
OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\data"
os.makedirs(OUT_DIR, exist_ok=True)

MAX_REINTENTOS = 5


def descargar_lote(url, max_reintentos=5):
    """Intenta descargar un lote con reintentos automaticos."""
    for intento in range(1, max_reintentos + 1):
        try:
            with urllib.request.urlopen(url, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"    Intento {intento}/{max_reintentos} fallo: {e}")
            if intento < max_reintentos:
                print(f"    Esperando 10 segundos antes de reintentar...")
                time.sleep(10)
    return None


def descargar_capa():
    print(f"\n--- Descargando: {NOMBRE} ---")
    
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
        url = f"{BASE}/{LAYER_ID}/query?{params}"
        
        print(f"  Descargando lote desde offset={offset}...")
        
        datos = descargar_lote(url, MAX_REINTENTOS)
        
        if datos is None:
            print(f"  No se pudo descargar el lote. Guardando lo que hay...")
            break
        
        if "error" in datos:
            print(f"  Error del servicio: {datos['error']}")
            break
        
        batch = datos.get("features", [])
        todos.extend([f["attributes"] for f in batch])
        
        print(f"  Recibidos: {len(batch)} registros (total acumulado: {len(todos)})")
        
        # Guardado parcial por si falla despues
        if todos:
            ruta = os.path.join(OUT_DIR, f"live_{NOMBRE}.csv")
            with open(ruta, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=todos[0].keys())
                writer.writeheader()
                writer.writerows(todos)
        
        if len(batch) < PAGE:
            break
        
        offset += len(batch)
        time.sleep(1)  # Pausa mas larga entre lotes
    
    print(f"\n  Total final: {len(todos)} registros")
    print(f"  Guardado en: {os.path.join(OUT_DIR, f'live_{NOMBRE}.csv')}")


if __name__ == "__main__":
    descargar_capa()
    