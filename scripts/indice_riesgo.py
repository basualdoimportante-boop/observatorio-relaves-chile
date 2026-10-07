# ============================================================
# INDICE DE RIESGO PRELIMINAR
# Basado en estandares CDA (2013) y ANCOLD (2012)
# Documentacion metodologica completa incluida
# ============================================================

import pandas as pd
import numpy as np
import os

OUT_DIR = r"C:\Users\Martín\Desktop\RELAVES\output"

# ============================================================
# DOCUMENTACION METODOLOGICA
# ============================================================
"""
INDICE DE RIESGO PRELIMINAR - RELAVES CHILE

Este indice es una SIMPLIFICACION ADAPTADA de los estandares
internacionales CDA (Canadian Dam Association, 2013) y
ANCOLD (Australian National Committee on Large Dams, 2012).

El indice NO reemplaza un analisis geotecnico profesional.
Sirve para PRIORIZAR que depositos requieren investigacion
detallada, no para declarar que un deposito es "seguro"
o "peligroso" de forma definitiva.

--- FACTORES DEL INDICE ---

FACTOR 1: CONSECUENCIA (exposicion a poblados)
  Puntaje maximo: 4

  Razon de la simplificacion:
  - CDA y ANCOLD usan la Poblacion en Riesgo (PAR) como metrica
    principal de consecuencia.
  - Nosotros NO tenemos el PAR real (cuantas personas viven en
    la zona de inundacion si el tranque falla).
  - Usamos la DISTANCIA al caserio mas cercano como PROXY.
  - Esto subestima la consecuencia en valles estrechos donde
    una falla puede afectar a poblados lejanos rio abajo.
  - Esto sobreestima la consecuencia en zonas planas donde una
    falla no alcanzaria al poblado cercano.

  Escala:
    MUY_ALTA (<500 m)    = 4 puntos  (CDA: "Extreme")
    ALTA (500m - 2km)    = 3 puntos  (CDA: "Very High")
    MEDIA (2-5 km)       = 2 puntos  (CDA: "High")
    BAJA (5-10 km)       = 1 punto   (CDA: "Significant")
    MUY_BAJA (>10 km)    = 0 puntos  (CDA: "Low")

FACTOR 2: PROBABILIDAD DE FALLA (metodo constructivo + estado)
  Puntaje maximo: 4

  Razon de la simplificacion:
  - ANCOLD clasifica el riesgo por metodo constructivo y
    consecuencia.
  - "Aguas arriba" es el metodo mas peligroso (licuefaccion
    sismica). Prohibido en Chile desde 1970 (D.S. N°86).
  - "Aguas abajo" es el mas seguro.
  - El estado del deposito (activo/inactivo/abandonado) modifica
    el riesgo: un deposito abandonado no tiene mantenimiento.
  - NO tenemos datos de contenido de solidos (si es espesado,
    en pasta o convencional), lo que afecta la estabilidad.
  - NO tenemos datos de la edad exacta del deposito.

  Escala:
    AGUAS ARRIBA + ABANDONADO  = 4 puntos
    AGUAS ARRIBA + INACTIVO    = 3 puntos
    EJE CENTRAL + ABANDONADO   = 3 puntos
    SIN DATO + ABANDONADO/INACTIVO = 3 puntos (precaucion)
    EJE CENTRAL + INACTIVO     = 2 puntos
    AGUAS ABAJO + ABANDONADO   = 2 puntos
    AGUAS ABAJO + INACTIVO     = 1 punto
    NO APLICA (cualquier estado) = 1 punto
    SIN DATO + ACTIVO          = 1 punto
    AGUAS ABAJO + ACTIVO       = 0 puntos

FACTOR 3: ESCALA (tonelaje)
  Puntaje maximo: 3

  Razon de la simplificacion:
  - El tonelaje determina la magnitud del impacto si hay falla.
  - CDA y ANCOLD no usan tonelaje directamente, pero si el
    volumen del deposito como factor de magnitud.
  - NO tenemos datos de la altura del muro, que es un factor
    critico en la evaluacion de ruptura.

  Escala:
    >1.000 Mt       = 3 puntos
    100-1.000 Mt    = 2 puntos
    10-100 Mt       = 1 punto
    <10 Mt          = 0 puntos

PUNTAJE MAXIMO TOTAL: 11 puntos

--- LIMITACIONES DEL INDICE ---

1. NO incluye sismicidad (pendiente: agregar capa de peligro
   sismico del CSN).
2. NO incluye precipitacion extrema (pendiente: agregar CHIRPS
   de Google Earth Engine).
3. NO incluye reologia del relave (contenido de solidos,
   granulometria).
4. NO incluye altura del muro.
5. NO incluye historial de incidentes.
6. NO incluye datos actualizados de monitoreo post-2020.
7. Las distancias a caserios son en linea recta, no por
   caminos o cauces.
"""
# ============================================================

print("=" * 75)
print("INDICE DE RIESGO PRELIMINAR")
print("=" * 75)

# ------------------------------------------------------------
# 1. CARGAR DATOS
# ------------------------------------------------------------
df = pd.read_csv(os.path.join(OUT_DIR, "ranking_con_exposicion.csv"))
print(f"\nDepositos a analizar: {len(df)}")

# ------------------------------------------------------------
# 2. FACTOR 1: CONSECUENCIA (exposicion a poblados)
# ------------------------------------------------------------
print("\n[1/3] Calculando factor de consecuencia...")

puntaje_exposicion = {
    "MUY_ALTA": 4,
    "ALTA": 3,
    "MEDIA": 2,
    "BAJA": 1,
    "MUY_BAJA": 0,
    "DESCONOCIDA": 2,  # Valor intermedio si no se pudo calcular
}

df["puntaje_consecuencia"] = df["exposicion_poblados"].map(puntaje_exposicion)
df["puntaje_consecuencia"] = df["puntaje_consecuencia"].fillna(2)

print(f"  Distribucion de puntajes:")
print(df["puntaje_consecuencia"].value_counts().sort_index(ascending=False).to_string())

# ------------------------------------------------------------
# 3. FACTOR 2: PROBABILIDAD DE FALLA
# ------------------------------------------------------------
print("\n[2/3] Calculando factor de probabilidad de falla...")

def calcular_puntaje_falla(row):
    """Calcula puntaje segun metodo constructivo y estado."""
    metodo = str(row["METODO_CONSTRUCTIVO_MURO"]).strip().upper()
    estado = str(row["cat_estado"]).strip().upper()
    
    # Metodos con aguas arriba
    if "AGUAS ARRIBA" in metodo or "AGUAS_ARRIBA" in metodo:
        if estado == "ABANDONADO":
            return 4
        elif estado == "INACTIVO":
            return 3
        else:
            return 2  # Activo con aguas arriba (raro)
    
    # Metodos con eje central
    if "EJE CENTRAL" in metodo or "EJE_CENTRAL" in metodo:
        if estado == "ABANDONADO":
            return 3
        elif estado == "INACTIVO":
            return 2
        else:
            return 1
    
    # Metodos con aguas abajo
    if "AGUAS ABAJO" in metodo or "AGUAS_ABAJO" in metodo:
        if estado == "ABANDONADO":
            return 2
        elif estado == "INACTIVO":
            return 1
        else:
            return 0
    
    # NO APLICA (filtrado, pasta, espesado)
    if "NO APLICA" in metodo:
        return 1
    
    # Sin dato o vacio
    if metodo in ["NAN", "", "NONE"]:
        if estado in ["ABANDONADO", "INACTIVO"]:
            return 3
        else:
            return 1
    
    # Otros metodos no clasificados
    return 2  # Valor conservador

df["puntaje_falla"] = df.apply(calcular_puntaje_falla, axis=1)

print(f"  Distribucion de puntajes:")
print(df["puntaje_falla"].value_counts().sort_index(ascending=False).to_string())

# ------------------------------------------------------------
# 4. FACTOR 3: ESCALA (tonelaje)
# ------------------------------------------------------------
print("\n[3/3] Calculando factor de escala...")

def calcular_puntaje_escala(tonelaje):
    if pd.isna(tonelaje):
        return 0
    if tonelaje >= 1_000_000_000:
        return 3
    elif tonelaje >= 100_000_000:
        return 2
    elif tonelaje >= 10_000_000:
        return 1
    else:
        return 0

df["puntaje_escala"] = df["cat_tonelaje_autorizado"].apply(calcular_puntaje_escala)

print(f"  Distribucion de puntajes:")
print(df["puntaje_escala"].value_counts().sort_index(ascending=False).to_string())

# ------------------------------------------------------------
# 5. INDICE TOTAL
# ------------------------------------------------------------
df["indice_riesgo"] = (
    df["puntaje_consecuencia"] +
    df["puntaje_falla"] +
    df["puntaje_escala"]
)

# Clasificacion
def clasificar_riesgo(indice):
    if indice >= 9:
        return "EXTREMO"
    elif indice >= 7:
        return "MUY_ALTO"
    elif indice >= 5:
        return "ALTO"
    elif indice >= 3:
        return "MEDIO"
    else:
        return "BAJO"

df["nivel_riesgo"] = df["indice_riesgo"].apply(clasificar_riesgo)

# ------------------------------------------------------------
# 6. REPORTE
# ------------------------------------------------------------
print("\n" + "=" * 75)
print("RESULTADOS DEL INDICE DE RIESGO")
print("=" * 75)

print("\nDistribucion por nivel de riesgo:")
for nivel in ["EXTREMO", "MUY_ALTO", "ALTO", "MEDIO", "BAJO"]:
    cant = (df["nivel_riesgo"] == nivel).sum()
    pct = 100 * cant / len(df)
    print(f"  {nivel:<12}: {cant:>3} ({pct:.1f}%)")

print(f"\nRango del indice: {df['indice_riesgo'].min()} a {df['indice_riesgo'].max()}")
print(f"Mediana: {df['indice_riesgo'].median():.1f}")

# Top 25 depositos con mayor riesgo
print("\n" + "=" * 75)
print("TOP 25 DEPOSITOS CON MAYOR RIESGO PRELIMINAR")
print("=" * 75)

top_riesgo = df.nlargest(25, "indice_riesgo")[
    ["cat_id", "cat_nombre_faena", "cat_tonelaje_autorizado",
     "METODO_CONSTRUCTIVO_MURO", "cat_estado", "exposicion_poblados",
     "distancia_caserio_m", "puntaje_consecuencia", "puntaje_falla",
     "puntaje_escala", "indice_riesgo", "nivel_riesgo"]
].copy()
top_riesgo["tonelaje_Mt"] = (top_riesgo["cat_tonelaje_autorizado"] / 1e6).round(1)

print(f"\n{'#':<3} {'ID':<11} {'Faena':<28} {'Mt':>7} {'Metodo':<15} {'Estado':<12} {'Expos':<10} {'Índ':>4}")
print("-" * 105)
for i, (_, row) in enumerate(top_riesgo.iterrows(), 1):
    faena = str(row["cat_nombre_faena"])[:26]
    metodo = str(row["METODO_CONSTRUCTIVO_MURO"])[:13]
    estado = str(row["cat_estado"])[:10]
    expo = str(row["exposicion_poblados"])[:8]
    print(f"{i:<3} {row['cat_id']:<11} {faena:<28} {row['tonelaje_Mt']:>7.1f} {metodo:<15} {estado:<12} {expo:<10} {row['indice_riesgo']:>4}")

# ------------------------------------------------------------
# 7. GUARDAR
# ------------------------------------------------------------
ruta = os.path.join(OUT_DIR, "ranking_con_riesgo.csv")
df.to_csv(ruta, index=False, encoding="utf-8")
print(f"\nArchivo guardado en: {ruta}")

# Guardar documentacion metodologica en archivo aparte
doc = """
DOCUMENTACION METODOLOGICA - INDICE DE RIESGO PRELIMINAR
============================================================

1. FUENTES DE REFERENCIA
   - Canadian Dam Association (CDA). Dam Safety Guidelines. 2013.
   - Australian National Committee on Large Dams (ANCOLD).
     Guidelines on Tailings Dams. 2012.
   - Servicio Nacional de Geologia y Mineria (SERNAGEOMIN).
     Catastro de Depositos de Relaves. Octubre 2025.

2. FACTORES DEL INDICE (maximo 11 puntos)
   
   Factor 1: Consecuencia (max 4 puntos)
     Proxy: distancia al caserio mas cercano.
     Limitacion: no usa Poblacion en Riesgo (PAR) real.
   
   Factor 2: Probabilidad de falla (max 4 puntos)
     Basado en metodo constructivo + estado.
     Limitacion: no incluye contenido de solidos ni altura de muro.
   
   Factor 3: Escala (max 3 puntos)
     Basado en tonelaje.
     Limitacion: no incluye altura del muro.

3. LIMITACIONES GENERALES
   - No incluye sismicidad.
   - No incluye precipitacion extrema.
   - No incluye reologia (contenido de solidos).
   - No incluye historial de incidentes.
   - Distancias en linea recta (no por cauces).

4. CLASIFICACION DE NIVELES
   EXTREMO:   indice >= 9
   MUY_ALTO:  indice 7-8
   ALTO:      indice 5-6
   MEDIO:     indice 3-4
   BAJO:      indice 0-2

5. USO DEL INDICE
   Este indice es una HERRAMIENTA DE PRIORIZACION.
   No reemplaza una evaluacion geotecnica profesional.
   Debe actualizarse cuando se incorporen sismicidad y precipitacion.
"""

ruta_doc = os.path.join(OUT_DIR, "DOCUMENTACION_INDICE_RIESGO.txt")
with open(ruta_doc, "w", encoding="utf-8") as f:
    f.write(doc)
print(f"Documentacion guardada en: {ruta_doc}")