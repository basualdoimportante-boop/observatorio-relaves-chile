# Observatorio de Relaves de Chile

Análisis integrado de riesgo y potencial económico de 109 depósitos de relaves mineros en Chile, usando datos abiertos de SERNAGEOMIN, el Centro Sismológico Nacional, CHIRPS e IDE Chile.

## Motivación

Chile tiene **839 depósitos de relaves catastrados** que acumulan más de **27.000 millones de toneladas** de residuos mineros. Muchos de ellos son pasivos ambientales abandonados sin responsable legal claro, y otros contienen concentraciones significativas de metales críticos como cobalto, níquel y tierras raras.

Este proyecto construye una **herramienta de priorización** que combina:

1. **Riesgo** (exposición a poblados, método constructivo, sismicidad, precipitación extrema).
2. **Potencial económico** (elementos enriquecidos respecto a la corteza terrestre).
3. **Antigüedad y estado** (factores de vulnerabilidad estructural).

El resultado es un dashboard interactivo que clasifica los depósitos en 4 categorías de decisión.

## Hallazgos principales

### Matriz de decisión

| Categoría | Depósitos | Descripción |
|---|---|---|
| **Prioridad máxima** | 18 | Alto potencial + alto riesgo |
| **Prioridad remediación** | 17 | Alto riesgo sin potencial económico |
| **Prioridad económica** | 44 | Alto potencial sin riesgo alto |
| **Baja prioridad** | 30 | Ni potencial ni riesgo |

### Casos críticos por riesgo a personas

De los 109 depósitos analizados, **11 amenazan directamente a comunidades** (a menos de 2 km de un caserío poblado):

| Depósito | Región | Distancia a poblado | Población | Método | Estado |
|---|---|---|---|---|---|
| **Las Cenizas Cabildo (0707-5C)** | Valparaíso | 1.851 m | 119 | **Aguas arriba** | **Abandonado** |
| **Faena Tambillos (0368-4N)** | Coquimbo | 1.881 m | **467** | **Aguas arriba** | Inactivo |
| **Altos de Punitaqui (0452-4N)** | Coquimbo | **118 m** | 43 | Eje central | Inactivo |
| Planta Ovalle (0020-4N) | Coquimbo | 1.025 m | 171 | Sin dato | **Abandonado** |
| Alhué (0766-RM) | Metropolitana | 1.859 m | 283 | Sin dato | Inactivo |

### Casos críticos por tonelaje + sismicidad

- **Andina (0065-5C)** — 210 Mt, aprobado en 1978, amenaza sísmica alta.
- **Escondida (0031-2N)** — 480 Mt, aprobado en 1993.
- **Los Bronces (0703-RM)** — 1.000 Mt, en la Región Metropolitana.

### Casos críticos por precipitación extrema

- **El Teniente (0076-6C)** — 132 mm en un solo día (el máximo del catastro).
- **El Soldado (0697-5C)** — 80 Mt con 119 mm/día.
- **Alhué (0766-RM)** — 114 mm/día con 8,8 Mt.

## Metodología

### Datos utilizados

| Dato | Fuente | Cobertura |
|---|---|---|
| Catastro de relaves | SERNAGEOMIN (oct 2025) | 839 depósitos |
| Geoquímica de superficie | SERNAGEOMIN (mar 2023) | 2.131 muestras |
| Amenaza sísmica | Centro Sismológico Nacional | Grilla nacional, SA(0.3) |
| Precipitación diaria | CHIRPS (Google Earth Engine) | 2015-2024, resolución 5,5 km |
| Caseríos | INE / IDE Chile (Censo 2017) | 3.669 asentamientos |

### Cruce de datos

La geoquímica y el catastro se cruzaron por **comuna + distancia UTM** (tolerancia de 500 m), logrando **98,9% de cobertura**. Los casos fuera de tolerancia se investigaron individualmente.

### Índice de riesgo (0 a 11)

Adaptado de los estándares internacionales:

- **Canadian Dam Association (2013)** — Clasificación por población en riesgo.
- **ANCOLD (2012)** — Clasificación por método constructivo.

Composición:

| Factor | Puntaje | Fundamento |
|---|---|---|
| Consecuencia (exposición a poblados) | 0-4 | CDA 2013 |
| Probabilidad de falla (método + estado) | 0-4 | ANCOLD 2012 |
| Escala (tonelaje) | 0-3 | Magnitud del impacto |

### Factor de Enriquecimiento

Se calculó el Factor de Enriquecimiento (EF) para 26 elementos, comparando la concentración en el relave con la concentración en la corteza continental superior (Rudnick & Gao 2003).

Solo se consideraron elementos con **menos del 10% de valores bajo el límite de detección**, para evitar sesgos por censura.

## Dashboard interactivo

El proyecto incluye un dashboard web construido con **Dash + Plotly** con las siguientes funciones:

- Mapa interactivo con zoom y capa opcional de caseríos.
- 3 modos de visualización: riesgo, potencial económico y categoría de decisión.
- Filtros clicables por tarjeta de categoría.
- Rombos dorados que marcan depósitos con alertas graves.
- Bloque colapsable con fuentes, metodología y glosario.

### Ejecución local

```bash
# Clonar el repositorio
git clone https://github.com/[tu-usuario]/observatorio-relaves-chile.git
cd observatorio-relaves-chile

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el dashboard
python dashboard/app.py