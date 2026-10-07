# ============================================================
# OBSERVATORIO DE RELAVES DE CHILE - version 10
# Jitter + rombos para alertas graves + fuentes y glosario
# Autor: Martin Basualdo
# ============================================================

import logging
import os
from pathlib import Path

import dash
from dash import dcc, html, Input, Output, State, ctx
import numpy as np
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ------------------------------------------------------------
# RUTAS
# ------------------------------------------------------------
CARPETA_BASE = Path(__file__).resolve().parent.parent
RUTA_DATOS = CARPETA_BASE / "output" / "ranking_final_integrado.csv"
RUTA_CASERIOS = CARPETA_BASE / "data" / "caserios_2017" / "Caserios_2017.shp"

# ------------------------------------------------------------
# CARGA DE RELAVES
# ------------------------------------------------------------
COLUMNAS_REQUERIDAS = [
    "LATITUD", "LONGITUD", "cat_nombre_faena", "cat_tonelaje_autorizado",
    "indice_riesgo", "potencial_total", "cat_id", "cat_estado", "REGION",
    "alertas_activas", "n_ree_enriquecidas", "categoria_decision",
]

if not RUTA_DATOS.exists():
    raise FileNotFoundError(f"No existe el archivo de datos: {RUTA_DATOS}")

df = pd.read_csv(RUTA_DATOS)

faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
if faltantes:
    raise ValueError(f"Faltan columnas en el archivo de datos: {faltantes}")

df = df.rename(columns={
    "LATITUD": "lat",
    "LONGITUD": "lon",
    "cat_nombre_faena": "faena",
    "cat_tonelaje_autorizado": "tonelaje",
    "indice_riesgo": "riesgo",
    "potencial_total": "potencial",
})

df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
df["riesgo"] = pd.to_numeric(df["riesgo"], errors="coerce").fillna(0)
df["potencial"] = pd.to_numeric(df["potencial"], errors="coerce").fillna(0)
df["tonelaje"] = pd.to_numeric(df["tonelaje"], errors="coerce").fillna(0)

filas_antes = len(df)
df = df.dropna(subset=["lat", "lon"]).copy()
filas_ok = df["lat"].between(-56, -17) & df["lon"].between(-76, -66)
df = df[filas_ok].copy()
if len(df) < filas_antes:
    log.warning(f"Descartadas {filas_antes - len(df)} filas por coordenadas inválidas")

df["tonelaje_mt"] = df["tonelaje"] / 1e6
df["tamano"] = df["tonelaje_mt"].apply(
    lambda x: max(5, min(40, (x ** 0.3) * 5)) if x > 0 else 5
)

COLUMNAS_TEXTO = ["faena", "cat_id", "cat_estado", "REGION",
                  "alertas_activas", "categoria_decision"]
for columna in COLUMNAS_TEXTO:
    df[columna] = df[columna].fillna("Sin información").astype(str)

df["n_ree_enriquecidas"] = pd.to_numeric(
    df["n_ree_enriquecidas"], errors="coerce"
).fillna(0)

# ------------------------------------------------------------
# JITTER: separar visualmente depósitos con mismo nombre
# ------------------------------------------------------------
def aplicar_jitter(dataframe, radio=0.0008, seed=42):
    """
    Desplaza levemente los depósitos que comparten el mismo nombre de faena
    para evitar superposición de markers en el mapa.
    """
    rng = np.random.default_rng(seed)
    df_out = dataframe.copy()

    nombres = df_out["faena"].fillna("").str.upper().str.strip()
    grupos = nombres[nombres.duplicated(keep=False) & (nombres != "")]

    df_out["lat_original"] = df_out["lat"]
    df_out["lon_original"] = df_out["lon"]
    df_out["jitter_aplicado"] = False

    if len(grupos) == 0:
        return df_out

    for nombre in grupos.unique():
        mask = nombres == nombre
        n = int(mask.sum())
        if n < 2:
            continue
        angulos = np.linspace(0, 2 * np.pi, n, endpoint=False)
        indices = df_out[mask].index.tolist()
        for i, idx in enumerate(indices):
            offset_lat = radio * np.sin(angulos[i])
            offset_lon = radio * np.cos(angulos[i])
            df_out.at[idx, "lat"] = df_out.at[idx, "lat"] + offset_lat
            df_out.at[idx, "lon"] = df_out.at[idx, "lon"] + offset_lon
            df_out.at[idx, "jitter_aplicado"] = True

    return df_out


df = aplicar_jitter(df)
n_jitter = int(df["jitter_aplicado"].sum())
log.info(f"Jitter aplicado a {n_jitter} depósitos con nombre duplicado")

# ------------------------------------------------------------
# IDENTIFICAR DEPÓSITOS CON ALERTAS GRAVES
# ------------------------------------------------------------
ALERTAS_GRAVES = [
    "AGUAS_ARRIBA",
    "SISMICA_MUY_ALTA",
    "SISMICA_CRITICA",
]

def tiene_alerta_grave(fila):
    alertas = str(fila.get("alertas_activas", ""))
    return any(a in alertas for a in ALERTAS_GRAVES)

df["alerta_grave"] = df.apply(tiene_alerta_grave, axis=1)
N_ALERTAS_GRAVES = int(df["alerta_grave"].sum())
log.info(f"Depósitos con alertas graves: {N_ALERTAS_GRAVES}")

TOTAL_DEPOSITOS = len(df)
log.info(f"Depósitos cargados: {TOTAL_DEPOSITOS}")

RESUMEN_CATEGORIAS = df["categoria_decision"].value_counts().to_dict()

# ------------------------------------------------------------
# CARGA DE CASERÍOS (opcional)
# ------------------------------------------------------------
def cargar_caserios(ruta):
    try:
        import geopandas as gpd
        gdf = gpd.read_file(ruta)
        gdf_proj = gdf.to_crs(epsg=32719)
        centroides_proj = gdf_proj.geometry.centroid
        centroides = centroides_proj.to_crs(epsg=4326)
        datos = pd.DataFrame({
            "lat": centroides.y,
            "lon": centroides.x,
            "nombre": gdf["NOM_LOC"].fillna("Sin nombre").astype(str),
            "poblacion": pd.to_numeric(
                gdf["TOT_PERSON"], errors="coerce"
            ).fillna(0),
        })
        datos["tamano"] = datos["poblacion"].apply(
            lambda x: max(5, min(20, (x ** 0.4) * 1.5)) if x > 0 else 4
        )
        log.info(f"Caseríos cargados: {len(datos)}")
        return datos
    except Exception as e:
        log.exception(f"No se pudo cargar caseríos: {e}")
        return None


caserios = cargar_caserios(RUTA_CASERIOS)
CASERIOS_DISPONIBLES = caserios is not None

# ------------------------------------------------------------
# CATEGORÍAS (Paleta Okabe-Ito)
# ------------------------------------------------------------
CATEGORIAS = {
    "PRIORIDAD_MAXIMA": {
        "etiqueta": "Prioridad máxima",
        "color": "#D55E00",
    },
    "PRIORIDAD_REMEDIACION": {
        "etiqueta": "Prioridad remediación",
        "color": "#E69F00",
    },
    "PRIORIDAD_ECONOMICA": {
        "etiqueta": "Prioridad económica",
        "color": "#0072B2",
    },
    "BAJA_PRIORIDAD": {
        "etiqueta": "Baja prioridad",
        "color": "#999999",
    },
}

# ------------------------------------------------------------
# CONFIGURACIÓN DE MODOS
# ------------------------------------------------------------
MODOS = {
    "riesgo": {
        "titulo": "Índice de riesgo general (0 a 11)",
        "color": "riesgo",
        "tipo": "continuo",
        "escala": "YlOrRd",
        "rango": [0, 11],
        "campos": [
            ("Faena", "faena", "", False, ""),
            ("Identificador", "cat_id", "", False, ""),
            ("Región", "REGION", "", False, ""),
            ("Tonelaje", "tonelaje_mt", ":.1f", False, " millones de toneladas"),
            ("Estado", "cat_estado", "", False, ""),
            ("Puntaje de riesgo", "riesgo", "", True, " / 11"),
            ("Alertas", "alertas_activas", "", False, ""),
        ],
        "explicacion": lambda: html.Div([
            html.B("Puntaje de riesgo (0 a 11): "),
            "suma de 3 factores: ",
            html.B("consecuencia "), "(exposición a poblados, 0 a 4), ",
            html.B("probabilidad de falla "), "(método más estado, 0 a 4) y ",
            html.B("escala "), "(tonelaje, 0 a 3). ",
            "A mayor rojo, mayor prioridad de investigación. ",
            html.B("Los rombos dorados "),
            "marcan depósitos con alertas graves (método aguas arriba, ",
            "sismicidad crítica o amenaza sísmica muy alta). ",
            html.B("No es una medida absoluta de seguridad."),
        ]),
    },
    "potencial": {
        "titulo": "Potencial económico (cantidad de elementos enriquecidos)",
        "color": "potencial",
        "tipo": "continuo",
        "escala": "Viridis",
        "rango": None,
        "campos": [
            ("Faena", "faena", "", False, ""),
            ("Identificador", "cat_id", "", False, ""),
            ("Región", "REGION", "", False, ""),
            ("Tonelaje", "tonelaje_mt", ":.1f", False, " millones de toneladas"),
            ("Elementos enriquecidos", "potencial", "", True, ""),
            ("Tierras raras", "n_ree_enriquecidas", ":.0f", False, ""),
        ],
        "explicacion": lambda: html.Div([
            html.B("Potencial económico: "),
            "cantidad de elementos químicos con Factor de Enriquecimiento mayor a 2 ",
            "respecto a la corteza terrestre. Incluye metales base (cobre, zinc, plomo), ",
            "elementos críticos (vanadio, escandio, uranio) y tierras raras. ",
            "Más elementos significa mayor atractivo para recuperación.",
        ]),
    },
    "categoria": {
        "titulo": "Categoría de decisión",
        "color": "categoria_decision",
        "tipo": "discreto",
        "colores": {k: v["color"] for k, v in CATEGORIAS.items()},
        "campos": [
            ("Faena", "faena", "", False, ""),
            ("Identificador", "cat_id", "", False, ""),
            ("Región", "REGION", "", False, ""),
            ("Tonelaje", "tonelaje_mt", ":.1f", False, " millones de toneladas"),
            ("Riesgo", "riesgo", "", False, " / 11"),
            ("Potencial", "potencial", "", False, " elementos"),
            ("Categoría", "categoria_decision", "", True, ""),
        ],
        "explicacion": lambda: html.Div([
            html.B("Categorías de decisión: "),
            html.B("Prioridad máxima ", style={"color": CATEGORIAS["PRIORIDAD_MAXIMA"]["color"]}),
            "(alto potencial y alto riesgo), ",
            html.B("Prioridad remediación ", style={"color": CATEGORIAS["PRIORIDAD_REMEDIACION"]["color"]}),
            "(alto riesgo sin potencial económico), ",
            html.B("Prioridad económica ", style={"color": CATEGORIAS["PRIORIDAD_ECONOMICA"]["color"]}),
            "(alto potencial sin riesgo alto), ",
            html.B("Baja prioridad ", style={"color": CATEGORIAS["BAJA_PRIORIDAD"]["color"]}),
            "(ni potencial ni riesgo).",
        ]),
    },
}


def construir_plantilla(campos):
    lineas = []
    for i, (etiqueta, _, formato, negrita, sufijo) in enumerate(campos):
        valor = f"%{{customdata[{i}]{formato}}}{sufijo}"
        if i == 0:
            lineas.append(f"<b>{valor}</b>")
        else:
            linea = f"{etiqueta}: {valor}"
            lineas.append(f"<b>{linea}</b>" if negrita else linea)
    return "<br>".join(lineas) + "<extra></extra>"


# ------------------------------------------------------------
# FUENTES DE DATOS
# ------------------------------------------------------------
FUENTES = [
    {
        "titulo": "Catastro de Depósitos de Relaves (octubre 2025)",
        "institucion": "SERNAGEOMIN - Servicio Nacional de Geología y Minería",
        "uso": "Ubicación, tonelaje, estado y método constructivo de los 839 depósitos.",
        "link": "https://www.sernageomin.cl/plataforma-publica-de-relaves/",
    },
    {
        "titulo": "Caracterización Geoquímica de Relaves (marzo 2023)",
        "institucion": "SERNAGEOMIN",
        "uso": "Concentración de 56 elementos en 2.131 muestras de superficie.",
        "link": "https://www.sernageomin.cl/plataforma-publica-de-relaves/",
    },
    {
        "titulo": "Mapa de Amenaza Sísmica de Chile (MASCSN26)",
        "institucion": "Centro Sismológico Nacional - Universidad de Chile",
        "uso": "Aceleración espectral SA(0.3) para período de retorno de 2.475 años.",
        "link": "https://www.csn.uchile.cl/",
    },
    {
        "titulo": "CHIRPS Daily (Climate Hazards Group Infrared Precipitation)",
        "institucion": "UCSB / Google Earth Engine",
        "uso": "Precipitación diaria 2015-2024, resolución 5,5 km.",
        "link": "https://www.chc.ucsb.edu/data/chirps",
    },
    {
        "titulo": "Caseríos Censo 2017",
        "institucion": "Instituto Nacional de Estadísticas (INE) / IDE Chile",
        "uso": "Ubicación y población de 3.669 asentamientos rurales.",
        "link": "https://www.ide.cl/",
    },
    {
        "titulo": "Dam Safety Guidelines (2013)",
        "institucion": "Canadian Dam Association",
        "uso": "Clasificación de consecuencia por población en riesgo.",
        "link": "https://www.cda.ca/",
    },
    {
        "titulo": "Guidelines on Tailings Dams (2012)",
        "institucion": "Australian National Committee on Large Dams (ANCOLD)",
        "uso": "Clasificación de riesgo por método constructivo y consecuencia.",
        "link": "https://www.ancold.org.au/",
    },
]

GLOSARIO = [
    ("Relave", "Residuo sólido finamente molido que queda tras extraer el mineral de interés de una operación minera."),
    ("Depósito de relaves", "Obra de ingeniería diseñada para almacenar relaves de forma segura."),
    ("Faena", "Conjunto de instalaciones mineras que operan bajo una misma administración."),
    ("Caserío", "Asentamiento humano rural pequeño, con población generalmente inferior a 300 habitantes."),
    ("Factor de Enriquecimiento (EF)", "Cuántas veces más concentrado está un elemento en el relave respecto a su concentración normal en la corteza terrestre."),
    ("Tierras raras", "Grupo de 14 elementos químicos usados en tecnología (imanes, baterías, pantallas). Escasos y valiosos."),
    ("Elementos críticos", "Elementos con riesgo de suministro y alta importancia económica (cobalto, litio, tierras raras, etc.)."),
    ("Amenaza sísmica", "Probabilidad de que ocurra un sismo de cierta intensidad en un lugar y período determinados."),
    ("Método constructivo aguas arriba", "Método de construcción de tranques de relaves prohibido en Chile desde 1970 por su alta vulnerabilidad a licuefacción sísmica."),
    ("Licuefacción", "Fenómeno en el que un suelo saturado pierde resistencia y se comporta como líquido durante un sismo."),
]


def construir_fuentes():
    items = []
    for f in FUENTES:
        items.append(
            html.Div([
                html.Div(f["titulo"], style={"fontWeight": "bold", "color": "#2c3e50"}),
                html.Div(f["institucion"], style={"fontSize": "13px", "color": "#555"}),
                html.Div(f["uso"], style={"fontSize": "12px", "color": "#777", "marginTop": "3px"}),
                html.A("Ver fuente oficial", href=f["link"], target="_blank",
                       style={"fontSize": "12px", "color": "#0072B2"}),
            ], style={"marginBottom": "12px", "paddingBottom": "10px",
                      "borderBottom": "1px solid #eee"})
        )
    return html.Div(items)


def construir_glosario():
    items = []
    for termino, definicion in GLOSARIO:
        items.append(
            html.Div([
                html.B(termino, style={"color": "#2c3e50"}),
                html.Span(": " + definicion, style={"color": "#555"}),
            ], style={"marginBottom": "8px", "fontSize": "13px"})
        )
    return html.Div(items)


def construir_metodologia():
    return html.Div([
        html.P("El índice de riesgo (0 a 11) es una simplificación adaptada de los estándares internacionales CDA (2013) y ANCOLD (2012). Se compone de tres factores:"),
        html.Ul([
            html.Li([html.B("Consecuencia (0-4): "), "basada en la distancia al caserío más cercano y su población. Referencia: CDA 2013, Tabla 2-1."]),
            html.Li([html.B("Probabilidad de falla (0-4): "), "según método constructivo y estado del depósito. Referencia: ANCOLD 2012."]),
            html.Li([html.B("Escala (0-3): "), "basada en el tonelaje autorizado. A mayor tonelaje, mayor impacto potencial si ocurre una falla."]),
        ], style={"fontSize": "13px", "color": "#555"}),
        html.P([
            html.B("Advertencia: "),
            "este índice es una herramienta de priorización. No reemplaza una evaluación geotécnica profesional ni constituye una medida absoluta de seguridad.",
        ], style={"fontSize": "13px", "color": "#c0392b", "marginTop": "10px"}),
    ])


# ------------------------------------------------------------
# TARJETAS CLICKEABLES
# ------------------------------------------------------------
def construir_contadores():
    tarjetas = []
    for clave, info in CATEGORIAS.items():
        cantidad = RESUMEN_CATEGORIAS.get(clave, 0)
        tarjetas.append(
            html.Button(
                id={"type": "tarjeta-categoria", "categoria": clave},
                n_clicks=0,
                children=[
                    html.Div(str(cantidad),
                             style={"fontSize": "28px", "fontWeight": "bold",
                                    "color": info["color"], "lineHeight": "1"}),
                    html.Div(info["etiqueta"],
                             style={"fontSize": "12px", "color": "#444",
                                    "marginTop": "4px"}),
                ],
                style={
                    "display": "inline-block",
                    "padding": "12px 20px",
                    "margin": "0 10px 10px 0",
                    "backgroundColor": "#ffffff",
                    "border": f"2px solid {info['color']}",
                    "borderRadius": "6px",
                    "textAlign": "center",
                    "minWidth": "140px",
                    "cursor": "pointer",
                    "fontFamily": "inherit",
                },
            )
        )

    tarjetas.append(
        html.Button(
            id="boton-ver-todas",
            n_clicks=0,
            children=[
                html.Div("Limpiar",
                         style={"fontSize": "14px", "fontWeight": "bold",
                                "color": "#444"}),
                html.Div("filtro",
                         style={"fontSize": "12px", "color": "#666",
                                "marginTop": "4px"}),
            ],
            style={
                "display": "inline-block",
                "padding": "12px 20px",
                "margin": "0 10px 10px 0",
                "backgroundColor": "#ffffff",
                "border": "2px dashed #aaa",
                "borderRadius": "6px",
                "textAlign": "center",
                "minWidth": "100px",
                "cursor": "pointer",
                "fontFamily": "inherit",
            },
        )
    )

    return html.Div(tarjetas, style={
        "padding": "15px 20px",
        "backgroundColor": "#f8f9fa",
        "borderBottom": "1px solid #dee2e6",
        "display": "flex",
        "flexWrap": "wrap",
    })


# ------------------------------------------------------------
# APLICACIÓN
# ------------------------------------------------------------
app = dash.Dash(__name__)
app.title = "Observatorio de Relaves de Chile"
server = app.server

opciones_capas = []
if CASERIOS_DISPONIBLES:
    opciones_capas.append(
        {"label": " Mostrar caseríos (poblaciones)", "value": "caserios"}
    )

app.layout = html.Div([
    dcc.Store(id="filtro-categoria", data=None, storage_type="memory"),

    html.Div([
        html.H1("Observatorio de Relaves de Chile",
                style={"color": "#2c3e50", "marginBottom": "5px"}),
        html.P(id="subtitulo",
               children=f"Análisis de riesgo y potencial económico de {TOTAL_DEPOSITOS} "
                        "depósitos de relaves (mayores o iguales a 1 millón de toneladas)",
               style={"color": "#5a6670", "marginTop": "0"}),
    ], style={"padding": "20px", "backgroundColor": "#ecf0f1",
              "borderBottom": "3px solid #3498db"}),

    construir_contadores(),

    html.Div([
        html.Label("Modo de visualización:",
                   style={"fontWeight": "bold", "marginRight": "15px"}),
        dcc.RadioItems(
            id="modo",
            options=[
                {"label": " Riesgo", "value": "riesgo"},
                {"label": " Potencial económico", "value": "potencial"},
                {"label": " Nivel de decisión", "value": "categoria"},
            ],
            value="riesgo",
            inline=True,
        ),
        html.Label("  |  Capas:",
                   style={"fontWeight": "bold", "marginLeft": "20px",
                          "marginRight": "10px"}),
        dcc.Checklist(
            id="capas",
            options=opciones_capas if opciones_capas else [
                {"label": " (caseríos no disponibles)", "value": "caserios",
                 "disabled": True}
            ],
            value=[],
            inline=True,
            style={"display": "inline-block"},
        ),
    ], style={"padding": "15px", "backgroundColor": "#f8f9fa",
              "borderBottom": "1px solid #dee2e6"}),

    html.Div(id="panel-explicacion",
             style={"padding": "12px 20px", "backgroundColor": "#fff8e1",
                    "borderLeft": "4px solid #f39c12",
                    "margin": "10px 20px", "fontSize": "14px",
                    "color": "#333", "maxHeight": "140px",
                    "overflowY": "auto"}),

    dcc.Graph(
        id="mapa",
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "displaylogo": False,
            "doubleClick": "reset",
        },
        style={"height": "68vh"},
    ),

    html.Details([
        html.Summary("📚 Fuentes, metodología y glosario",
                     style={"cursor": "pointer", "padding": "12px",
                            "fontWeight": "bold", "color": "#2c3e50",
                            "backgroundColor": "#e8f4f8",
                            "borderRadius": "4px",
                            "marginBottom": "10px"}),
        html.Div([
            html.H3("Fuentes de datos", style={"color": "#0072B2"}),
            construir_fuentes(),

            html.H3("Metodología del índice de riesgo",
                    style={"color": "#0072B2", "marginTop": "20px"}),
            construir_metodologia(),

            html.H3("Glosario de términos",
                    style={"color": "#0072B2", "marginTop": "20px"}),
            construir_glosario(),
        ], style={"padding": "15px", "backgroundColor": "#fafafa",
                  "border": "1px solid #ddd", "borderRadius": "4px"}),
    ], style={"margin": "10px 20px"}),

    html.Div([
        html.P([
            "Observatorio de Relaves de Chile · ",
            "Datos abiertos de SERNAGEOMIN, CSN, CHIRPS e IDE Chile · ",
            "Proyecto de portafolio sin fines de lucro · ",
            "Licencia MIT",
        ], style={"textAlign": "center", "fontSize": "12px",
                  "color": "#666", "margin": "0"}),
    ], style={"padding": "20px", "backgroundColor": "#ecf0f1",
              "borderTop": "1px solid #dee2e6"}),

], style={"fontFamily": "Arial, sans-serif", "margin": "0"})


# ------------------------------------------------------------
# CALLBACK 1: filtro de categorías
# ------------------------------------------------------------
@app.callback(
    Output("filtro-categoria", "data"),
    [Input({"type": "tarjeta-categoria", "categoria": dash.ALL}, "n_clicks"),
     Input("boton-ver-todas", "n_clicks")],
    [State("filtro-categoria", "data")],
    prevent_initial_call=True,
)
def actualizar_filtro(clicks_tarjetas, click_ver_todas, filtro_actual):
    trigger_id = ctx.triggered_id

    if trigger_id == "boton-ver-todas":
        return None

    if isinstance(trigger_id, dict) and trigger_id.get("type") == "tarjeta-categoria":
        categoria = trigger_id.get("categoria")
        if filtro_actual == categoria:
            return None
        return categoria

    return filtro_actual


# ------------------------------------------------------------
# CALLBACK 2: mapa
# ------------------------------------------------------------
@app.callback(
    [Output("mapa", "figure"),
     Output("panel-explicacion", "children"),
     Output("subtitulo", "children")],
    [Input("modo", "value"),
     Input("capas", "value"),
     Input("filtro-categoria", "data")],
)
def actualizar_mapa(modo, capas, filtro_categoria):
    config = MODOS.get(modo, MODOS["riesgo"])
    capas = capas or []
    campos = config["campos"]
    columnas_custom = [col for (_, col, _, _, _) in campos]
    plantilla = construir_plantilla(campos)

    if filtro_categoria is not None:
        df_mostrar = df[df["categoria_decision"] == filtro_categoria].copy()
        etiqueta = CATEGORIAS.get(filtro_categoria, {}).get("etiqueta", filtro_categoria)
        subtitulo = (f"Mostrando {len(df_mostrar)} depósitos en la categoría "
                     f"'{etiqueta}' (de {TOTAL_DEPOSITOS} totales). "
                     "Haz clic de nuevo en la tarjeta para ver todos.")
    else:
        df_mostrar = df
        subtitulo = (f"Análisis de riesgo y potencial económico de {TOTAL_DEPOSITOS} "
                     "depósitos de relaves (mayores o iguales a 1 millón de toneladas)")

    args_grafico = {
        "data_frame": df_mostrar,
        "lat": "lat",
        "lon": "lon",
        "size": "tamano",
        "custom_data": columnas_custom,
        "title": config["titulo"],
        "zoom": 5,
        "center": {"lat": -33, "lon": -71},
        "map_style": "carto-positron",
        "size_max": 40,
    }

    if config["tipo"] == "continuo":
        args_grafico["color"] = config["color"]
        args_grafico["color_continuous_scale"] = config["escala"]
        if config["rango"] is not None:
            args_grafico["range_color"] = config["rango"]
    else:
        args_grafico["color"] = config["color"]
        args_grafico["color_discrete_map"] = config["colores"]

    fig = px.scatter_map(**args_grafico)
    fig.update_traces(hovertemplate=plantilla)

    # Capa: depósitos con alertas graves (rombos dorados)
    df_graves = df_mostrar[df_mostrar["alerta_grave"]]
    if len(df_graves) > 0:
        fig.add_scattermap(
            lat=df_graves["lat"],
            lon=df_graves["lon"],
            mode="markers",
            marker=dict(
                size=14,
                color="#FFD700",
                symbol="diamond",
            ),
            name=f"Alertas graves ({len(df_graves)})",
            text=df_graves["faena"],
            customdata=df_graves[["cat_id", "alertas_activas"]].values,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "ID: %{customdata[0]}<br>"
                "<b>Alertas graves: %{customdata[1]}</b>"
                "<extra></extra>"
            ),
            showlegend=True,
        )

    # Capa: caseríos (opcional)
    if "caserios" in capas and CASERIOS_DISPONIBLES:
        fig.add_scattermap(
            lat=caserios["lat"],
            lon=caserios["lon"],
            mode="markers",
            marker=dict(
                size=caserios["tamano"],
                color="rgba(52, 73, 94, 0.4)",
            ),
            name="Caseríos",
            text=caserios["nombre"],
            customdata=caserios[["poblacion"]].values,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Población: %{customdata[0]:,.0f} habitantes"
                "<extra></extra>"
            ),
            showlegend=True,
        )

    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.85)",
        ),
    )

    return fig, config["explicacion"](), subtitulo


# ------------------------------------------------------------
# EJECUTAR
# ------------------------------------------------------------
if __name__ == "__main__":
    debug = os.getenv("DASH_DEBUG") == "1"
    log.info(f"Arrancando dashboard (debug={debug})")
    app.run(debug=debug)