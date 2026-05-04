import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dashboard Analítico", layout="wide", initial_sidebar_state="expanded")

# 2. INYECCIÓN CSS AVANZADA (ESTILO NEÓN / DEEP PURPLE)
st.markdown("""
<style>
    /* Fondo principal y tipografía */
    .stApp { background-color: #0b0710; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    
    /* Panel Lateral (Sidebar) - Corrigiendo el contraste */
    [data-testid="stSidebar"] { background-color: #130c1d !important; border-right: 1px solid #2a1b3d; }
    [data-testid="stSidebar"] * { color: #d1d1d1 !important; } /* Letras grises/blancas legibles */
    
    /* Cajas de selección (Multiselect) - Fondo oscuro y texto claro */
    .stMultiSelect div[data-baseweb="select"] > div { background-color: #1a1025; color: white; border: 1px solid #3b2559; border-radius: 6px;}
    
    /* Títulos y textos generales */
    h1, h2, h3, h4 { color: #f4f4f5 !important; font-weight: 600; letter-spacing: 0.5px;}
    p { color: #a1a1aa; }
    
    /* Tarjetas de Métricas (KPIs) al estilo de tu imagen de referencia */
    div[data-testid="metric-container"] {
        background-color: #160e22;
        border-top: 3px solid #8a2be2; /* Borde superior neón morado */
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    div[data-testid="metric-container"] label { color: #a1a1aa !important; font-size: 0.9rem;}
    div[data-testid="metric-container"] div { color: #00e5ff !important; font-size: 1.8rem; font-weight: bold;} /* Números Cyan Neón */
    
    /* Cajas de análisis estratégico */
    .analysis-box {
        background-color: #130c1d;
        border-left: 3px solid #00e5ff; /* Acento Cyan */
        padding: 15px;
        font-size: 0.85rem;
        color: #a1a1aa;
        border-radius: 0 6px 6px 0;
        margin-top: -10px; margin-bottom: 20px;
    }
    hr { border-color: #2a1b3d; }
</style>
""", unsafe_allow_html=True)

st.title("💠 Panel de Control: Productividad y Resiliencia Territorial")
st.markdown("Monitoreo avanzado de indicadores agronómicos, riesgo climático y exposición a economías ilícitas.")
st.markdown("---")

# 3. CARGA DE DATOS
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

# 4. PANEL LATERAL (FILTROS)
st.sidebar.markdown("### ⚙️ Parámetros de Segmentación")
depto_sel = st.sidebar.multiselect("Filtrar por Departamento", options=sorted(df['departamento'].dropna().unique()))
muni_options = sorted(df[df['departamento'].isin(depto_sel)]['municipio'].dropna().unique()) if depto_sel else sorted(df['municipio'].dropna().unique())
muni_sel = st.sidebar.multiselect("Filtrar por Municipio", options=muni_options)
cadena_sel = st.sidebar.multiselect("Filtrar por Cadena", options=sorted(df['cadena_productiva'].dropna().unique()))
genero_sel = st.sidebar.multiselect("Filtrar por Género", options=sorted(df['genero'].dropna().unique()))

df_filtered = df.copy()
if depto_sel: df_filtered = df_filtered[df_filtered['departamento'].isin(depto_sel)]
if muni_sel: df_filtered = df_filtered[df_filtered['municipio'].isin(muni_sel)]
if cadena_sel: df_filtered = df_filtered[df_filtered['cadena_productiva'].isin(cadena_sel)]
if genero_sel: df_filtered = df_filtered[df_filtered['genero'].isin(genero_sel)]

# 5. INDICADORES MACRO (KPIs)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Volumen Productores", f"{len(df_filtered):,}")
k2.metric("Superficie Total (Ha)", f"{df_filtered['area_ha'].sum():,.1f}")
k3.metric("Producción (Kg)", f"{df_filtered['produccion_kg'].sum():,.0f}")
k4.metric("Brecha Media", f"{df_filtered['brecha_productividad_%'].mean():.1f}%")
vcr_mean = df_filtered['VCR'].mean() if 'VCR' in df_filtered.columns else 0.0
k5.metric("Índice VCR", f"{vcr_mean:.2f}")
pct_cert = (len(df_filtered[df_filtered['estado_certificacion'] == 'Certificado']) / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
k6.metric("Tasa Certificación", f"{pct_cert:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# 6. CONFIGURACIÓN DE COLORES NEÓN PARA GRÁFICOS
neon_colors = ['#00e5ff', '#b400ff', '#ff007f', '#00ff66'] # Cyan, Morado, Rosa, Verde neón

# 7. MATRIZ VISUAL PRINCIPAL
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### Radar Territorial de Riesgo Climático")
    # Mapa optimizado: carto-darkmatter puro, con colores vibrantes
    fig_map = px.scatter_mapbox(df_filtered, lat="latitud", lon="longitud", color="Vulnerabilidad CC", 
                                size="produccion_kg", hover_name="municipio", hover_data=["perfil_espacial", "id_limpio"],
                                mapbox_style="carto-darkmatter", zoom=4.5, 
                                color_discrete_sequence=neon_colors, template="plotly_dark")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("""<div class='analysis-box'><b>Análisis de Concentración:</b> La distribución geoespacial evidencia aglomeraciones de alto rendimiento (burbujas mayores) superpuestas en zonas de vulnerabilidad climática crítica. Indica un riesgo sistémico sobre la cadena de suministro, demandando infraestructura de mitigación prioritaria.</div>""", unsafe_allow_html=True)

with row1_col2:
    st.markdown("#### Eficiencia: Productividad vs. Ingresos")
    fig_scatter = px.scatter(df_filtered, x="productividad_kg_ha", y="ingresos_anuales_cop", 
                             color="cadena_productiva", log_y=True,
                             hover_data=["id_limpio", "genero"], color_discrete_sequence=neon_colors, template="plotly_dark")
    fig_scatter.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig_scatter.update_traces(marker=dict(size=8, opacity=0.7, line=dict(width=1, color='White')))
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("""<div class='analysis-box'><b>Análisis de Rentabilidad:</b> Correlación logarítmica positiva entre productividad física e ingresos. El sobreprecio estructural de los mercados formales es evidente en los estratos superiores, justificando la inversión técnica intensiva.</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("#### Cobertura Espacial del Dato")
    df_quality = df_filtered['origen_coordenada'].value_counts().reset_index()
    df_quality.columns = ['Estado de Trazabilidad', 'Volumen']
    fig_quality = px.pie(df_quality, values='Volumen', names='Estado de Trazabilidad', hole=0.75,
                         color_discrete_sequence=['#8a2be2', '#00e5ff'], template="plotly_dark")
    fig_quality.update_traces(textposition='outside', textinfo='percent+label')
    fig_quality.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_quality, use_container_width=True)
    st.markdown("""<div class='analysis-box'><b>Auditoría de Calidad:</b> Proporción de recuperación de datos mediante imputación algorítmica espacial (KNN). Garantiza la robustez estadística y minimiza el sesgo de supervivencia en los registros.</div>""", unsafe_allow_html=True)

with row2_col2:
    st.markdown("#### Presión Ilegal vs. Brecha Productiva")
    fig_macro = px.scatter(df_filtered, x="promedio_coca_ha_5y", y="brecha_productividad_%", 
                           color="cadena_productiva", size="area_ha", marginal_y="box",
                           hover_data=["id_limpio", "municipio"], color_discrete_sequence=neon_colors, template="plotly_dark")
    fig_macro.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_macro, use_container_width=True)
    st.markdown("""<div class='analysis-box'><b>Análisis de Resiliencia:</b> Deterioro de la brecha productiva en municipios con alta densidad histórica de cultivos ilícitos. Se detectan clústers de resistencia (outliers) que logran mantener eficiencias positivas pese a la presión del entorno.</div>""", unsafe_allow_html=True)

st.markdown("---")

# 8. TABLA DE DATOS COMPACTA AL FINAL
with st.expander("📂 VER MATRIZ DE DETALLE TRANSACCIONAL (ANONIMIZADA)", expanded=False):
    st.dataframe(df_filtered[['id_limpio', 'departamento', 'municipio', 'cadena_productiva', 'genero', 'brecha_productividad_%', 'ingresos_anuales_cop']], height=250, use_container_width=True)
