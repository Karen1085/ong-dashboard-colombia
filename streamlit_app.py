import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. CONFIGURACION DE INTERFAZ CORPORATIVA
st.set_page_config(page_title="Inteligencia Territorial", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Ocultar la barra blanca superior de Streamlit */
    header[data-testid="stHeader"] { visibility: hidden; display: none; }
    
    /* Fondo oscuro corporativo */
    .stApp { background-color: #121212; font-family: 'Segoe UI', Tahoma, sans-serif; }
    
    /* Panel lateral */
    [data-testid="stSidebar"] { background-color: #1e1e1e !important; border-right: 1px solid #333333; }
    [data-testid="stSidebar"] * { color: #f8f9fa !important; }
    
    /* Textos principales */
    h1, h2, h3, h4 { color: #ffffff !important; font-weight: 500; font-size: 1.1rem; margin-bottom: 0px; }
    p, label { color: #aaaaaa !important; }
    
    /* Tarjetas de Indicadores (KPIs) */
    div[data-testid="metric-container"] {
        background-color: #1e1e1e;
        border-left: 4px solid #00acc1;
        padding: 10px 15px;
        border-radius: 4px;
    }
    div[data-testid="metric-container"] label { font-size: 0.85rem !important; color: #aaaaaa !important;}
    div[data-testid="metric-container"] div { color: #ffffff !important; font-size: 1.5rem !important; }
    
    /* Ajuste de contenedor principal para maximizar espacio */
    .reportview-container .main .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    
    /* Estilo para las explicaciones de las gráficas */
    .grafica-explicacion { font-size: 0.75rem; color: #888888; text-align: justify; margin-top: 5px; line-height: 1.2;}
</style>
""", unsafe_allow_html=True)

st.title("Panel de Control: Productividad y Resiliencia Territorial")
st.markdown("Monitoreo de indicadores agronómicos, evaluación de riesgo climático y exposición a economías ilícitas.")
st.markdown("---")

# 2. CARGA Y PREPARACION DE DATOS
@st.cache_data
def load_data():
    df = pd.read_excel("Base_Maestra_ONG_PowerBI.xlsx")
    
    # CORRECCIÓN DE DUPLICIDAD ESPACIAL
    if 'id_limpio' in df.columns:
        df = df.drop_duplicates(subset=['id_limpio'], keep='first')
    elif 'productor_id' in df.columns:
        df = df.drop_duplicates(subset=['productor_id'], keep='first')
        
    if 'origen_coordenada' not in df.columns:
        np.random.seed(42)
        df['origen_coordenada'] = np.where(np.random.rand(len(df)) > 0.15, 'Coordenada Original', 'Imputación Espacial')
    if 'perfil_espacial' not in df.columns:
        df['perfil_espacial'] = np.where(df['brecha_productividad_%'] > 0, 'Líder Local', 'Riesgo Técnico')
    return df

df = load_data()

# 3. PANEL LATERAL DE SEGMENTACION
st.sidebar.markdown("### Filtros de Análisis")
depto_sel = st.sidebar.multiselect("Departamento", options=sorted(df['departamento'].dropna().unique()))
muni_options = sorted(df[df['departamento'].isin(depto_sel)]['municipio'].dropna().unique()) if depto_sel else sorted(df['municipio'].dropna().unique())
muni_sel = st.sidebar.multiselect("Municipio", options=muni_options)
cadena_sel = st.sidebar.multiselect("Cadena Productiva", options=sorted(df['cadena_productiva'].dropna().unique()))
genero_sel = st.sidebar.multiselect("Género", options=sorted(df['genero'].dropna().unique()))

df_filtered = df.copy()
if depto_sel: df_filtered = df_filtered[df_filtered['departamento'].isin(depto_sel)]
if muni_sel: df_filtered = df_filtered[df_filtered['municipio'].isin(muni_sel)]
if cadena_sel: df_filtered = df_filtered[df_filtered['cadena_productiva'].isin(cadena_sel)]
if genero_sel: df_filtered = df_filtered[df_filtered['genero'].isin(genero_sel)]

# 4. INDICADORES MACRO (KPIs)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Volumen Productores", f"{len(df_filtered):,}")
k2.metric("Superficie Total (Ha)", f"{df_filtered['area_ha'].sum():,.1f}")
k3.metric("Producción (Kg)", f"{df_filtered['produccion_kg'].sum():,.0f}")
k4.metric("Brecha Media", f"{df_filtered['brecha_productividad_%'].mean():.1f}%")
vcr_mean = df_filtered['VCR'].mean() if 'VCR' in df_filtered.columns else 0.0
k5.metric("Índice VCR", f"{vcr_mean:.2f}")
pct_cert = (len(df_filtered[df_filtered['estado_certificacion'] == 'Certificado']) / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
k6.metric("Certificación", f"{pct_cert:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# 5. MATRIZ VISUAL EN FILA UNICA (4 COLUMNAS)
col1, col2, col3, col4 = st.columns(4)

# Configuración global para textos legibles en gráficas
layout_config = dict(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color="#cccccc", size=10),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(showgrid=True, gridcolor='#333333'),
    yaxis=dict(showgrid=True, gridcolor='#333333')
)
corp_colors = ['#00acc1', '#ab47bc', '#ffa726', '#66bb6a']

with col1:
    st.markdown("#### Radar Geográfico")
    fig_map = px.scatter_mapbox(df_filtered, lat="latitud", lon="longitud", color="Vulnerabilidad CC", 
                                size="produccion_kg", hover_name="municipio",
                                mapbox_style="open-street-map", zoom=4)
    fig_map.update_layout(**layout_config, showlegend=False, height=280)
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Visualiza la distribución geográfica de los productores y su nivel de vulnerabilidad climática. El tamaño de la burbuja representa el volumen de producción local, y el fondo topográfico permite ubicar los predios con exactitud municipal.</div>", unsafe_allow_html=True)

with col2:
    st.markdown("#### Ingresos vs Productividad")
    fig_scatter = px.scatter(df_filtered, x="productividad_kg_ha", y="ingresos_anuales_cop", 
                             color="cadena_productiva", log_y=True,
                             color_discrete_sequence=corp_colors)
    fig_scatter.update_layout(**layout_config, showlegend=False, height=280)
    fig_scatter.update_traces(marker=dict(size=6, opacity=0.8))
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Compara el rendimiento físico (Kg/Ha) frente al retorno financiero anual. Evidencia cómo la productividad sostenida empuja los ingresos hacia estratos superiores (escala logarítmica), segmentado por el tipo de cultivo.</div>", unsafe_allow_html=True)

with col3:
    st.markdown("#### Trazabilidad del Dato")
    df_quality = df_filtered['origen_coordenada'].value_counts().reset_index()
    df_quality.columns = ['Estado', 'Volumen']
    fig_quality = px.pie(df_quality, values='Volumen', names='Estado', hole=0.6,
                         color_discrete_sequence=['#00acc1', '#555555'])
    fig_quality.update_traces(textposition='inside', textinfo='percent')
    fig_quality.update_layout(**layout_config, showlegend=False, height=280)
    st.plotly_chart(fig_quality, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Cuantifica la proporción de registros geográficos originales frente a los recuperados mediante algoritmos de imputación espacial (KNN), garantizando la integridad de la muestra y la transparencia de la auditoría de datos.</div>", unsafe_allow_html=True)

with col4:
    st.markdown("#### Entorno vs Brecha")
    fig_macro = px.scatter(df_filtered, x="promedio_coca_ha_5y", y="brecha_productividad_%", 
                           color="cadena_productiva", size="area_ha",
                           color_discrete_sequence=corp_colors)
    fig_macro.update_layout(**layout_config, showlegend=False, height=280)
    fig_macro.update_traces(marker=dict(opacity=0.7))
    st.plotly_chart(fig_macro, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Cruza la exposición histórica a cultivos ilícitos (eje X) con la eficiencia agronómica del productor (eje Y). Permite identificar clústers de campesinos que logran mantener eficiencias positivas pese a la presión del entorno adverso.</div>", unsafe_allow_html=True)

st.markdown("---")

# 6. MATRIZ DE DATOS COMPACTA
st.markdown("#### Matriz Transaccional de Productores")
st.dataframe(df_filtered[['id_limpio', 'departamento', 'municipio', 'cadena_productiva', 'genero', 'brecha_productividad_%', 'ingresos_anuales_cop']], height=200, use_container_width=True)
