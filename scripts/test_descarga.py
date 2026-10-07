# Prueba de descarga usando urllib (sin requests)
import urllib.request
import json

url = "https://services1.arcgis.com/OyjvVdFTl5hfSdX3/arcgis/rest/services/PLATAFORMA_PUBLICA_RELAVES_WFL1/FeatureServer/25/query?where=1%3D1&outFields=*&f=json&resultRecordCount=5&returnGeometry=false"

print("Conectando al servicio de SERNAGEOMIN...")

try:
    with urllib.request.urlopen(url, timeout=60) as response:
        datos = json.loads(response.read().decode("utf-8"))
    
    registros = datos.get("features", [])
    print(f"Registros recibidos: {len(registros)}")
    
    if registros:
        primero = registros[0]["attributes"]
        print(f"\nPrimer registro:")
        print(f"  ID: {primero.get('ID')}")
        print(f"  Nombre: {primero.get('NOMBRE_FAE')}")
        print(f"  Region: {primero.get('REGION')}")
        print(f"  Cobalto (Co): {primero.get('CON_CO')} g/t")
        print(f"  Niquel (Ni): {primero.get('CON_NI')} g/t")
        print(f"  Cobre (Cu): {primero.get('CON_CU')} g/t")
    
    print("\nFunciona correctamente.")

except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")