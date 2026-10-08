# Observatorio de Relaves de Chile

Análisis integrado de riesgo y potencial económico de 109 depósitos de relaves mineros en Chile, mediante datos abiertos de SERNAGEOMIN, Centro Sismológico Nacional, CHIRPS e IDE Chile.

**Dashboard público:** [https://observatorio-relaves-chile.onrender.com/](https://observatorio-relaves-chile.onrender.com/)

---

## Descripción

Chile es el mayor productor de cobre del mundo. Como consecuencia, acumula **839 depósitos de relaves catastrados** que en conjunto superan los **27.000 millones de toneladas** de residuos mineros. Muchos de ellos son pasivos ambientales abandonados sin responsable legal identificado, mientras otros contienen concentraciones significativas de metales críticos como cobalto, níquel y tierras raras.

Este proyecto construye una **herramienta de priorización** que clasifica los depósitos según tres dimensiones complementarias:

1. **Riesgo estructural y exposición** (método constructivo, estado, sismicidad, precipitación extrema y cercanía a poblados).
2. **Potencial económico** (elementos químicos enriquecidos respecto a la corteza terrestre).
3. **Antigüedad y estado operacional** (factores de vulnerabilidad acumulada).

El resultado es un dashboard interactivo, de acceso público, que clasifica los depósitos en cuatro categorías de decisión y documenta de forma verificable el estado de mitigación de los casos críticos.

---

## Contexto

La gestión de relaves en Chile está en un momento de transformación institucional. La **Agenda Nacional de Relaves 2025-2026**, impulsada por el **Ministerio de Minería**, estructuró tres líneas estratégicas:

| Línea | Enfoque |
|---|---|
| **Seguridad y fiscalización** | Monitoreo continuo, prohibición del método aguas arriba, criterios de diseño |
| **Economía circular y revalorización** | Reprocesamiento de relaves, recuperación de minerales críticos |
| **Remediación de pasivos** | Identificación y priorización de depósitos abandonados |

En paralelo, la Superintendencia del Medio Ambiente ha aumentado la fiscalización y existen programas activos de monitoreo satelital (InSAR), instrumentación piezométrica y plataformas públicas de información.

Sin embargo, persisten brechas documentadas: **3 de los 5 casos críticos identificados en este análisis no tienen planes de mitigación públicos ni monitoreo activo verificable**.

---

## Objetivos

### Objetivo general

Cuantificar y comunicar de forma verificable el riesgo, el potencial económico y el estado de mitigación de los depósitos de relaves de mayor relevancia en Chile, mediante análisis geoespacial reproducible y datos abiertos.

### Objetivos específicos

1. Integrar el catastro nacional de relaves con datos geoquímicos, sísmicos, climáticos y demográficos.
2. Construir un índice de riesgo adaptado de estándares internacionales (CDA 2013, ANCOLD 2012).
3. Calcular el Factor de Enriquecimiento de 26 elementos químicos respecto a la corteza terrestre.
4. Identificar los depósitos con mayor exposición a poblados y comunidades rurales.
5. Verificar el estado de mitigación, sanciones y monitoreo de los casos críticos.
6. Publicar los resultados en un dashboard interactivo de acceso público.

---

## Área de estudio

Análisis a escala nacional. Se analizaron **839 depósitos catastrados** por SERNAGEOMIN (octubre 2025) en las 16 regiones del país, con foco en las regiones con mayor concentración minera: Antofagasta, Atacama, Coquimbo, Valparaíso, Metropolitana y O'Higgins.

Para el análisis detallado se filtraron **109 depósitos con tonelaje ≥ 1 millón de toneladas**, que representan el **99% del tonelaje nacional catastrado**.

---

## Datos y fuentes

| Dato | Fuente | Cobertura |
|---|---|---|
| Catastro de relaves | SERNAGEOMIN (octubre 2025) | 839 depósitos |
| Geoquímica de superficie | SERNAGEOMIN (marzo 2023) | 2.131 muestras, 56 elementos |
| Amenaza sísmica | Centro Sismológico Nacional | Grilla nacional, SA(0.3) para TR 2.475 años |
| Precipitación diaria | CHIRPS (Google Earth Engine) | 2015-2024, resolución 5,5 km |
| Caseríos y población | INE / IDE Chile (Censo 2017) | 3.669 asentamientos rurales |
| Estándares de referencia | CDA (2013), ANCOLD (2012), Rudnick & Gao (2003) | Metodologías internacionales |

**Nota sobre accesibilidad:** Todos los datos utilizados son de acceso público y gratuito. Los scripts de descarga y procesamiento están en `scripts/`.

---

## Metodología

### 1. Cruce de datos

La geoquímica de superficie y el catastro físico se cruzaron por **comuna + distancia UTM** con una tolerancia de **500 metros**, logrando una cobertura del **98,9%** de las muestras. Los casos fuera de tolerancia se investigaron individualmente mediante revisión por nombre de faena y empresa.

### 2. Índice de riesgo (0 a 11)

Simplificación adaptada de estándares internacionales:

| Factor | Puntaje | Fundamento |
|---|---|---|
| **Consecuencia** (exposición a poblados) | 0-4 | CDA 2013, Tabla 2-1 |
| **Probabilidad de falla** (método + estado) | 0-4 | ANCOLD 2012 |
| **Escala** (tonelaje) | 0-3 | Magnitud del impacto |

### 3. Factor de Enriquecimiento (EF)

Se calculó el EF para **26 elementos** comparando la concentración en el relave con la concentración en la corteza continental superior (Rudnick & Gao 2003).

**Criterio de selección:** Solo se consideraron elementos con **menos del 10% de valores bajo el límite de detección**, para evitar sesgos por censura estadística. Esta decisión metodológica excluyó elementos como Sb, Bi, W y Mo, que presentan tasas de censura superiores al 25% y generan valores artificialmente inflados.

### 4. Alertas críticas

Se definieron tres condiciones que activan una marca visual independiente del índice de riesgo:

| Alerta | Criterio |
|---|---|
| `AGUAS_ARRIBA` | Método constructivo prohibido en Chile desde 1970 (DS N°86) |
| `SISMICA_MUY_ALTA` | SA(0.3) ≥ 1,8 g |
| `SISMICA_CRITICA` | Amenaza sísmica alta + antigüedad > 30 años |

---

## Resultados

### Matriz de decisión

| Categoría | Depósitos | Descripción |
|---|---|---|
| **Prioridad máxima** | 18 | Alto potencial + alto riesgo |
| **Prioridad remediación** | 17 | Alto riesgo sin potencial económico |
| **Prioridad económica** | 44 | Alto potencial sin riesgo alto |
| **Baja prioridad** | 30 | Ni potencial ni riesgo significativo |

### Depósitos con mayor riesgo a personas

De los 109 depósitos analizados, **11 se encuentran a menos de 2 km de un caserío poblado**:

| Depósito | Región | Distancia | Población | Método | Estado |
|---|---|---|---|---|---|
| **Las Cenizas Cabildo (0707-5C)** | Valparaíso | 1.851 m | 119 | **Aguas arriba** | **Abandonado** |
| **Faena Tambillos (0368-4N)** | Coquimbo | 1.881 m | **467** | **Aguas arriba** | Inactivo |
| **Altos de Punitaqui (0452-4N)** | Coquimbo | **118 m** | 43 | Eje central | Inactivo |
| Planta Ovalle (0020-4N) | Coquimbo | 1.025 m | 171 | Sin dato | **Abandonado** |
| Alhué (0766-RM) | Metropolitana | 1.859 m | 283 | Sin dato | Inactivo |

**Nota metodológica:** La distancia se calculó como distancia euclidiana al centroide del caserío más cercano. No considera la ruta hidrológica ni la dirección del flujo en caso de falla.

### Depósitos con mayor criticidad sísmica

- **Andina (0065-5C)** — 210 Mt, aprobado en 1978, amenaza sísmica alta.
- **Escondida (0031-2N)** — 480 Mt, aprobado en 1993.
- **Los Bronces (0703-RM)** — 1.000 Mt, en la Región Metropolitana.

### Depósitos con mayor precipitación extrema registrada

- **El Teniente (0076-6C)** — 132 mm en un solo día (máximo del catastro).
- **El Soldado (0697-5C)** — 80 Mt con 119 mm/día.
- **Alhué (0766-RM)** — 114 mm/día con 8,8 Mt.

---

## Estado de mitigación verificado

Se realizó una verificación exhaustiva del estado de mitigación, sanciones y monitoreo para los 5 depósitos con mayor riesgo a personas. Las fuentes utilizadas son exclusivamente oficiales: SERNAGEOMIN, SMA, SNIFA, SEIA y prensa especializada verificable.

### Resumen consolidado

| Depósito | Mitigación activa | Sanción SMA | Monitoreo verificado |
|---|---|---|---|
| Las Cenizas Cabildo | ✅ Plan de Invierno 2025 | ✅ Procedimiento D-176-2025 | ✅ Reporte a SNIFA |
| Faena Tambillos | ✅ Depósito relaves filtrados (RCA 32/2016) | ❌ No encontrado | ⚠️ Parcial |
| Altos de Punitaqui | ❌ No encontrado | ✅ Procedimiento D-040-2015 | ❌ No encontrado |
| Planta Ovalle (ENAMI) | ✅ Emergencia activa | ⚠️ En evolución | ✅ SENAPRED |
| Alhué | ❌ No encontrado | ❌ No encontrado | ❌ No encontrado |

**Hallazgo principal:** 3 de los 5 casos críticos **no tienen planes de mitigación públicos ni monitoreo activo verificable** al cierre de esta versión.

### Detalle por caso

**Las Cenizas Cabildo (Valparaíso)**
- Plan de Invierno autorizado por SERNAGEOMIN desde marzo de 2025.
- La SMA formuló 5 cargos en julio de 2025 por escurrimiento de aguas contaminadas ocurrido en junio de 2024.
- Expediente público en SNIFA (DFZ-2025-919-V-RCA).
- **Advertencia:** los cargos corresponden al evento de 2024, no al evento de julio de 2026.

**Faena Tambillos (Coquimbo)**
- Proyecto "Depósito de Relaves Filtrados CM Florida" con RCA N°32/2016.
- Extiende vida útil 7 años mediante sistema de relaves filtrados.
- **Advertencia:** la hipótesis inicial de "abandono" no se sostiene con la evidencia disponible. El depósito está operativo.

**Altos de Punitaqui (Coquimbo)**
- La SMA formuló cargos en agosto de 2015 (procedimiento D-040-2015).
- La empresa presentó un Programa de Cumplimiento.
- **No se encontró evidencia de plan de remediación posterior ni de monitoreo activo post-2015.**

**Planta Ovalle / ENAMI (Coquimbo)**
- Evento de julio 2026: más de 200 mm de lluvia provocaron sobrepaso del muro en 2 sectores.
- ENAMI activó procedimientos de emergencia (refuerzo de pretiles, bombas sumergibles).
- SENAPRED declaró perímetro de seguridad. Sernageomin detectó agrietamiento y erosión en 3 puntos del muro.
- **Capacidad:** 10 Mt autorizadas, 9,13 Mt depositadas (91%).

**Alhué (Región Metropolitana)**
- No se encontró información pública sobre un depósito inactivo en Alhué.
- **Advertencia:** el embalse Carén de Codelco está en Alhué, pero es un depósito activo con Plan de Cierre aprobado (Res. Ex. 409/2021) y de otra titularidad.

---

## Constancia de comunicación institucional

La información contenida en este repositorio y en el dashboard público **será comunicada** a las instituciones competentes en la gestión, fiscalización y prevención de riesgos asociados a depósitos de relaves en Chile.

### Instituciones destinatarias

| Ámbito | Institución |
|---|---|
| Fiscalización técnica minera | Servicio Nacional de Geología y Minería (SERNAGEOMIN) |
| Fiscalización ambiental | Superintendencia del Medio Ambiente (SMA) |
| Política pública minera | Ministerio de Minería |
| Prevención y respuesta | Servicio Nacional de Prevención y Respuesta ante Desastres (SENAPRED) |

### Contenido de la comunicación

- Enlace al dashboard público.
- Resumen de los 5 casos críticos identificados.
- Estado verificado de mitigación, sanciones y monitoreo.
- Oferta de datos crudos, metodología y código fuente para verificación independiente.

---

## Limitaciones

1. **El índice de riesgo es una herramienta de priorización**, no una evaluación geotécnica profesional.
2. **La exposición a poblados usa distancia euclidiana**, no por cauce hidrológico.
3. **Los datos de geoquímica son de superficie**, no de profundidad.
4. **La cobertura de estaciones DGA terminó en 2020.** La precipitación se calculó con datos satelitales CHIRPS.
5. **30 depósitos no tienen método constructivo registrado**, recibiendo un puntaje conservador por precaución.
6. **La verificación de mitigación depende de información pública disponible.** Es posible que existan planes no publicados.
7. **La Agenda Nacional de Relaves 2025-2026 está en implementación.** Algunas líneas no tienen evidencia pública de ejecución concreta al cierre de esta versión.

---

## Dashboard interactivo

Aplicación web construida con **Dash + Plotly** con las siguientes funciones:

- **Mapa interactivo** con zoom, capa opcional de caseríos y agrupación de depósitos con nombres duplicados.
- **3 modos de visualización:** riesgo, potencial económico y categoría de decisión.
- **Filtros clicables** por tarjeta de categoría.
- **Rombos dorados** que marcan los 34 depósitos con alertas graves.
- **Bloque colapsable** con fuentes, metodología y glosario.

**Dashboard en producción:** [https://observatorio-relaves-chile.onrender.com/](https://observatorio-relaves-chile.onrender.com/)

### Ejecución local

```bash
git clone https://github.com/basualdoimportante-boop/observatorio-relaves-chile.git
cd observatorio-relaves-chile

python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
python dashboard/app.py
```

Al ejecutar el comando, Dash mostrará en la terminal la dirección local donde está disponible la aplicación. Esa dirección es accesible únicamente desde el computador donde se ejecuta.

---

## Estructura del proyecto

```
observatorio-relaves-chile/
├── dashboard/
│   └── app.py                          # Dashboard en Dash
├── scripts/                            # Pipeline de análisis
│   ├── 01_explorar_catastro.py
│   ├── descargar_geoquimica.py
│   ├── cruce_completo.py
│   ├── construir_maestro.py
│   ├── analisis_final.py
│   ├── indice_riesgo.py
│   ├── alertas_criticas.py
│   ├── analisis_cercania.py
│   ├── analisis_sismico.py
│   ├── ranking_integrado.py
│   └── riesgo_personas.py
├── output/                             # Resultados finales
│   ├── ranking_final_integrado.csv     # Dataset principal
│   ├── riesgo_personas.csv
│   └── top40_ef_cobalto.csv
├── data/                               # Datos crudos (ignorados en Git)
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Líneas de trabajo abiertas

Estas son las líneas identificadas por el proyecto, disponibles para quien quiera continuarlas:

- Solicitud de expedientes de fiscalización, planes de cierre y denuncias de los 5 casos críticos vía Ley de Transparencia.
- Investigación de los 30 depósitos sin método constructivo registrado.
- Análisis temporal con series de precipitación más largas (30+ años con Landsat).
- Migración a arquitectura modular con `dash-pages` para nuevas vistas.
- Verificación de hallazgos con SERNAGEOMIN y SMA.
- Integración de formularios de denuncia ciudadana con moderación previa.

---

## Herramientas utilizadas

- **Google Earth Engine:** Procesamiento satelital en la nube (Sentinel-2, CHIRPS).
- **QGIS:** Gestión y exportación de datos vectoriales.
- **Python:** Análisis de datos (pandas, geopandas, numpy, plotly, dash).
- **GitHub:** Control de versiones y publicación del repositorio.
- **Render:** Despliegue del dashboard en producción.

---

## Autor

**Martín Basualdo**
- GitHub: [@basualdoimportante-boop](https://github.com/basualdoimportante-boop)
- Proyecto de portafolio en ciencia de datos geoespacial.

---

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Los datos originales pertenecen a sus respectivas instituciones (SERNAGEOMIN, CSN, INE, UCSB).

---

## Advertencia legal

Este es un **proyecto independiente de análisis de datos abiertos**. No tiene relación oficial con SERNAGEOMIN, el Ministerio de Minería, la SMA ni ninguna empresa minera. Las conclusiones son responsabilidad exclusiva del autor y deben ser verificadas con las instituciones competentes antes de tomar decisiones operativas o regulatorias.

Los expedientes sancionatorios están sujetos a actualización. Se recomienda consultar SNIFA directamente. Las instituciones mencionadas son organismos públicos cuyas vías de contacto están publicadas en sus sitios oficiales.