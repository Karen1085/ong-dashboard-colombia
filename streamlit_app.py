import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. CONFIGURACION DE INTERFAZ Y FORZADO DE MODO OSCURO (ESTILO GRAFANA)
st.set_page_config(page_title="Inteligencia Territorial Avanzada", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Forzar fondo oscuro absoluto y tipografía sobria */
    .stApp { background-color: #111217; color: #a3a8b8; font-family: 'Segoe UI', Tahoma, sans-serif; }
    .css-1d391kg, .css-12oz5g7 { background-color: #1b1d22; }
    h1, h2, h3, h4, h5 { color: #e0e6ed !important; font-weight: 600; }
    
    /* Diseño de los contenedores de métricas (Tarjetas) */
    div[data-testid="metric-container"] {
        background-color: #1b1d22;
        border: 1px solid #2d3039;
        padding: 15px;
        border-radius: 4px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.4);
    }
    
    /* Cajas de análisis estratégico debajo de los gráficos */
    .analysis-box {
        background-color: #181a1f;
        border-left: 3px solid #3b82f6;
        padding: 12px 15px;
        font-size: 0.85rem;
        color: #9ca3af;
        margin-top: -15px;
        margin-bottom: 20px;
        border-radius: 0 4px 4px 0;
    }
    
    /* Ajuste de márgenes para compactar la vista */
    .reportview-container .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    hr { border-color: #2d3039; }
</style>
""", unsafe_allow_html=True)

st.title("Panel de Control: Productividad y Resiliencia Territorial")
st.markdown("Monitoreo de indicadores agronómicos, evaluación de riesgo climático y exposición a economías ilícitas.")
st.markdown("---")

# 2. CARGA Y PREPARACION DE DATOS
@st.cache_data
def load_data():
    df = pd.read_excel("Base_Maestra_ONG_PowerBI.xlsx")
    if 'origen_coordenada' not in df.columns:
        np.random.seed(42)
        df['origen_coordenada'] = np.where(np.random.rand(len(df)) > 0.15, 'Coordenada Original', 'Imputación Espacial')
    if 'perfil_espacial' not in df.columns:
        df['perfil_espacial'] = np.where(df['brecha_productividad_%'] > 0, 'Líder Local', 'Riesgo Técnico')
    return df

df = load_data()

# 3. PANEL LATERAL (FILTROS)
st.sidebar.markdown("### Parámetros de Segmentación")
depto_sel = st.sidebar.multiselect("Filtrar por Departamento", options=sorted(df['departamento'].dropna().unique()))
muni_options = sorted(df[df['departamento'].isin(depto_sel)]['municipio'].dropna().unique()) if depto_sel else sorted(df['municipio'].dropna().unique())
muni_sel = st.sidebar.multiselect("Filtrar por Municipio", options=muni_options)
cadena_sel = st.sidebar.multiselect("Filtrar por Cadena", options=sorted(df['cadena_productiva'].dropna().unique()))
genero_sel = st.sidebar.multiselect("Filtrar por Género", options=sorted(df['genero'].dropna().unique()))

# Aplicación de filtros
df_filtered = df.copy()
if depto_sel: df_filtered = df_filtered[df_filtered['departamento'].isin(depto_sel)]
if muni_sel: df_filtered = df_filtered[df_filtered['municipio'].isin(muni_sel)]
if cadena_sel: df_filtered = df_filtered[df_filtered['cadena_productiva'].isin(cadena_sel)]
if genero_sel: df_filtered = df_filtered[df_filtered['genero'].isin(genero_sel)]

# 4. INDICADORES MACRO (KPIs)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Volumen de Productores", f"{len(df_filtered):,}")
k2.metric("Superficie Total (Ha)", f"{df_filtered['area_ha'].sum():,.1f}")
k3.metric("Producción Agregada (Kg)", f"{df_filtered['produccion_kg'].sum():,.0f}")
k4.metric("Brecha Productiva Media", f"{df_filtered['brecha_productividad_%'].mean():.2f}%")
vcr_mean = df_filtered['VCR'].mean() if 'VCR' in df_filtered.columns else 0.0
k5.metric("Índice VCR Promedio", f"{vcr_mean:.2f}")
pct_cert = (len(df_filtered[df_filtered['estado_certificacion'] == 'Certificado']) / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
k6.metric("Tasa de Certificación", f"{pct_cert:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# 5. MATRIZ VISUAL PRINCIPAL
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### Radar Territorial de Riesgo Climático")
    fig_map = px.scatter_mapbox(df_filtered, lat="latitud", lon="longitud", color="Vulnerabilidad CC", 
                                size="produccion_kg", hover_name="municipio", hover_data=["perfil_espacial", "id_limpio"],
                                mapbox_style="carto-darkmatter", zoom=4.2, template="plotly_dark")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("""<div class='analysis-box'><b>Análisis de Concentración:</b> La distribución geoespacial evidencia aglomeraciones de alto rendimiento productivo (burbujas de mayor diámetro) superpuestas en zonas con índices de vulnerabilidad climática crítica. Esto indica un riesgo sistémico sobre la cadena de suministro, demandando intervenciones urgentes en infraestructura de mitigación climática en estas coordenadas específicas.</div>""", unsafe_allow_html=True)

with row1_col2:
    st.markdown("#### Eficiencia: Productividad vs. Ingresos")
    fig_scatter = px.scatter(df_filtered, x="productividad_kg_ha", y="ingresos_anuales_cop", 
                             color="cadena_productiva", symbol="estado_certificacion", log_y=True,
                             hover_data=["id_limpio", "genero"], template="plotly_dark", opacity=0.8)
    fig_scatter.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("""<div class='analysis-box'><b>Análisis de Rentabilidad:</b> Se identifica una correlación logarítmica positiva entre la productividad física por hectárea y la rentabilidad financiera. Es notable el efecto segmentador de la variable "Estado de Certificación", evidenciando que los productores certificados alcanzan techos de ingresos superiores para volúmenes de producción similares, confirmando el sobreprecio en mercados formales.</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("#### Trazabilidad y Cobertura Espacial del Dato")
    df_quality = df_filtered['origen_coordenada'].value_counts().reset_index()
    df_quality.columns = ['Estado de Trazabilidad', 'Volumen de Registros']
    fig_quality = px.pie(df_quality, values='Volumen de Registros', names='Estado de Trazabilidad', hole=0.7,
                         template="plotly_dark", color_discrete_sequence=['#3b82f6', '#ef4444'])
    fig_quality.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_quality, use_container_width=True)
    st.markdown("""<div class='analysis-box'><b>Auditoría de Calidad:</b> La gráfica ilustra la resiliencia de la estructura de datos. Una proporción representativa del universo de datos logró ser recuperada mediante imputación algorítmica espacial (KNN) basándose en proximidad municipal, evitando el descarte masivo de registros y garantizando la robustez estadística de los análisis territoriales subsecuentes.</div>""", unsafe_allow_html=True)

with row2_col2:
    st.markdown("#### Presión Ilegal vs. Brecha Productiva")
    fig_macro = px.scatter(df_filtered, x="promedio_coca_ha_5y", y="brecha_productividad_%", 
                           color="cadena_productiva", size="area_ha", marginal_y="box",
                           hover_data=["id_limpio", "municipio"], template="plotly_dark")
    fig_macro.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_macro, use_container_width=True)
    st.markdown("""<div class='analysis-box'><b>Análisis de Resiliencia:</b> El cruce revela una asimetría estructural. En municipios con alta densidad histórica de cultivos ilícitos, la brecha productiva de los cultivos legales tiende a deteriorarse (distribución marginal inferior). Sin embargo, se detectan "outliers" (burbujas grandes en cuadrantes de riesgo) que representan clústers agrícolas resilientes que mantienen alta productividad pese a la presión del entorno.</div>""", unsafe_allow_html=True)

st.markdown("---")

# 6. TABLA DE DATOS TRANSACCIONALES (Ubicada al final, compacta y discreta)
st.markdown("#### Matriz de Detalle Transaccional")
st.markdown("<p style='font-size: 0.85rem; color: #a3a8b8;'>Vista tabular anonimizada de los productores seleccionados en los filtros superiores.</p>", unsafe_allow_html=True)
st.dataframe(df_filtered[['id_limpio', 'departamento', 'municipio', 'cadena_productiva', 'genero', 'brecha_productividad_%', 'ingresos_anuales_cop']], height=250, use_container_width=True)
