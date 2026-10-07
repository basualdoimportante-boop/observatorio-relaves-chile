# ============================================================
# SCRIPT 01: EXPLORAR EL CATASTRO DE RELAVES
# Objetivo: entender la estructura del archivo Excel antes de analizarlo
# ============================================================

# 1. Importar las librerías necesarias
import pandas as pd

# 2. Definir la ruta del archivo
ruta_catastro = r"C:\Users\Martín\Desktop\RELAVES\data\CATASTRO_RELAVES_CHILE_OCT2025.xlsx"

# 3. Cargar el archivo Excel
#    - sheet_name: la hoja que queremos leer
#    - header=6: los encabezados están en la fila 7 (índice 6 en Python)
df = pd.read_excel(
    ruta_catastro,
    sheet_name="CDR_CHILE",
    header=6
)

# 4. Mostrar información básica
print("=" * 60)
print("INFORMACIÓN BÁSICA DEL CATASTRO")
print("=" * 60)

# 4.1 Dimensiones: filas x columnas
print(f"\nDimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")

# 4.2 Nombres de todas las columnas
print(f"\nColumnas disponibles:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

# 4.3 Primeras 5 filas para ver el formato de los datos
print(f"\nPrimeras 5 filas:")
print(df.head())

# 4.4 Tipos de datos de cada columna
print(f"\nTipos de datos:")
print(df.dtypes)