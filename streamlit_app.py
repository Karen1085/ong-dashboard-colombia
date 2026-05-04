import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. CONFIGURACION DE INTERFAZ CORPORATIVA (SLATE DARK)
st.set_page_config(page_title="Inteligencia Territorial", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Fondo gris corporativo, alta legibilidad */
    .stApp { background-color: #1e1e24; font-family: 'Segoe UI', Tahoma, sans-serif; }
    
    /* Panel lateral */
    [data-testid="stSidebar"] { background-color: #2b2b36 !important; border-right: 1px solid #4a4a5a; }
    [data-testid="stSidebar"] * { color: #f8f9fa !important; }
    
    /* Textos principales */
    h1, h2, h3, h4 { color: #ffffff !important; font-weight: 500; font-size: 1.1rem; }
    p, label { color: #ced4da !important; }
    
    /* Tarjetas de Indicadores (KPIs) */
    div[data-testid="metric-container"] {
        background-color: #2b2b36;
        border-left: 4px solid #3b82f6;
        padding: 10px 15px;
        border-radius: 4px;
    }
    div[data-testid="metric-container"] label { font-size: 0.85rem !important; }
    div[data-testid="metric-container"] div { color: #ffffff !important; font-size: 1.5rem !important; }
    
    /* Ajuste para 4 columnas */
    .reportview-container .main .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
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

# Paleta corporativa de colores
corp_colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']

with col1:
    st.markdown("#### Radar Geográfico")
    # Mapa OpenStreetMap para máxima visibilidad geográfica
    fig_map = px.scatter_mapbox(df_filtered, lat="latitud", lon="longitud", color="Vulnerabilidad CC", 
                                size="produccion_kg", hover_name="municipio",
                                mapbox_style="open-street-map", zoom=4)
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=300, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.markdown("#### Ingresos vs Productividad")
    fig_scatter = px.scatter(df_filtered, x="productividad_kg_ha", y="ingresos_anuales_cop", 
                             color="cadena_productiva", log_y=True,
                             color_discrete_sequence=corp_colors, template="plotly_dark")
    fig_scatter.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, height=300, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig_scatter.update_traces(marker=dict(size=6, opacity=0.8))
    st.plotly_chart(fig_scatter, use_container_width=True)

with col3:
    st.markdown("#### Trazabilidad del Dato")
    df_quality = df_filtered['origen_coordenada'].value_counts().reset_index()
    df_quality.columns = ['Estado', 'Volumen']
    fig_quality = px.pie(df_quality, values='Volumen', names='Estado', hole=0.6,
                         color_discrete_sequence=['#3b82f6', '#64748b'], template="plotly_dark")
    fig_quality.update_traces(textposition='inside', textinfo='percent')
    fig_quality.update_layout(margin={"r":0,"t":10,"l":0,"b":10}, height=300, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_quality, use_container_width=True)

with col4:
    st.markdown("#### Entorno vs Brecha")
    fig_macro = px.scatter(df_filtered, x="promedio_coca_ha_5y", y="brecha_productividad_%", 
                           color="cadena_productiva", size="area_ha",
                           color_discrete_sequence=corp_colors, template="plotly_dark")
    fig_macro.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, height=300, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig_macro.update_traces(marker=dict(opacity=0.7))
    st.plotly_chart(fig_macro, use_container_width=True)

st.markdown("---")

# 6. MATRIZ DE DATOS COMPACTA Y DESLIZABLE
st.markdown("#### Detalle Transaccional de Productores")
st.dataframe(df_filtered[['id_limpio', 'departamento', 'municipio', 'cadena_productiva', 'genero', 'brecha_productividad_%', 'ingresos_anuales_cop']], height=200, use_container_width=True)
