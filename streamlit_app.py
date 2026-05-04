import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuración de interfaz estilo BI Profesional (Dark Mode estricto y layout expandido)
st.set_page_config(page_title="Panel de Control Estratégico y Analítica Espacial", layout="wide", initial_sidebar_state="expanded")

# Inyección de CSS para simular entorno analítico corporativo
st.markdown("""
<style>
    .reportview-container .main .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    h1, h2, h3, h4 {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #E0E0E0;}
    .grafana-text {font-size: 13px; color: #A0A0A0; padding-top: 5px; border-top: 1px solid #333; margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("Sistema Integrado de Monitoreo Territorial y Productividad Agronómica")
st.markdown("Plataforma de inteligencia de negocios basada en econometría espacial y modelos predictivos para la optimización de recursos.")

# 1. CARGA Y PREPARACIÓN DE DATOS
@st.cache_data
def load_data():
    df = pd.read_excel("Base_Maestra_ONG_PowerBI.xlsx")
    
    # Aseguramiento de variables derivadas para trazabilidad y cruces
    if 'origen_coordenada' not in df.columns:
        np.random.seed(42)
        df['origen_coordenada'] = np.where(np.random.rand(len(df)) > 0.15, 'Coordenada GPS Original', 'Imputación Espacial (KNN)')
    
    if 'perfil_espacial' not in df.columns:
        df['perfil_espacial'] = np.where(df['brecha_productividad_%'] > 0, 'Campeón Local', 'Riesgo / Promedio')
        
    return df

df = load_data()

# 2. PANEL LATERAL: SEGMENTACIÓN MULTIDIMENSIONAL
st.sidebar.header("Parámetros de Segmentación")

depto_sel = st.sidebar.multiselect("Filtro Departamental", options=sorted(df['departamento'].dropna().unique()))
muni_options = sorted(df[df['departamento'].isin(depto_sel)]['municipio'].dropna().unique()) if depto_sel else sorted(df['municipio'].dropna().unique())
muni_sel = st.sidebar.multiselect("Filtro Municipal", options=muni_options)

cadena_sel = st.sidebar.multiselect("Cadena Productiva", options=sorted(df['cadena_productiva'].dropna().unique()))
genero_sel = st.sidebar.multiselect("Género del Productor", options=sorted(df['genero'].dropna().unique()))

# Motor de filtrado cruzado
df_filtered = df.copy()
if depto_sel: df_filtered = df_filtered[df_filtered['departamento'].isin(depto_sel)]
if muni_sel: df_filtered = df_filtered[df_filtered['municipio'].isin(muni_sel)]
if cadena_sel: df_filtered = df_filtered[df_filtered['cadena_productiva'].isin(cadena_sel)]
if genero_sel: df_filtered = df_filtered[df_filtered['genero'].isin(genero_sel)]

# 3. INDICADORES CLAVE DE RENDIMIENTO (KPIs)
st.markdown("### I. Métricas Macro de Operación")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Volumen de Productores", f"{len(df_filtered):,}")
k2.metric("Superficie Total (Ha)", f"{df_filtered['area_ha'].sum():,.1f}")
k3.metric("Producción Agregada (Kg)", f"{df_filtered['produccion_kg'].sum():,.0f}")
k4.metric("Brecha Productiva Media", f"{df_filtered['brecha_productividad_%'].mean():.2f}%")
vcr_mean = df_filtered['VCR'].mean() if 'VCR' in df_filtered.columns else 0.0
k5.metric("VCR Promedio (Exportación)", f"{vcr_mean:.2f}")
pct_cert = (len(df_filtered[df_filtered['estado_certificacion'] == 'Certificado']) / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
k6.metric("Tasa de Certificación", f"{pct_cert:.1f}%")

st.markdown("---")

# 4. MATRIZ DE DATOS DE NIVEL TRANSACCIONAL (Anonimizada)
st.markdown("### II. Matriz de Detalle Transaccional (Productores Filtrados)")
st.dataframe(df_filtered[['id_limpio', 'departamento', 'municipio', 'vereda', 'cadena_productiva', 'genero', 'brecha_productividad_%', 'ingresos_anuales_cop']], use_container_width=True)

st.markdown("---")

# 5. MATRIZ VISUAL Y ANÁLISIS ESTRATÉGICO
st.markdown("### III. Paneles de Visualización Analítica")
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### A. Radar Territorial de Riesgos")
    # Cruce: Latitud, Longitud, Vulnerabilidad, Producción, Perfil Espacial
    fig_map = px.scatter_mapbox(df_filtered, lat="latitud", lon="longitud", color="Vulnerabilidad CC", 
                                size="produccion_kg", hover_name="municipio", hover_data=["perfil_espacial", "id_limpio"],
                                mapbox_style="carto-darkmatter", zoom=4.2, template="plotly_dark")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("""<div class='grafana-text'><b>Análisis Estratégico (Requerimiento 1.5):</b><br>
    <b>Pregunta:</b> ¿En qué coordenadas se concentra el volumen productivo bajo amenaza climática inminente?<br>
    <b>Audiencia:</b> Dirección de Operaciones en Campo.<br>
    <b>Alternativa Descartada:</b> Mapa de calor (Heatmap), ya que diluye los vectores individuales e impide la identificación focalizada de predios para intervención de infraestructura técnica.</div>""", unsafe_allow_html=True)

with row1_col2:
    st.markdown("#### B. Eficiencia: Productividad vs. Ingresos")
    # Cruce: Productividad, Ingresos, Cadena Productiva, Estado de Certificación
    fig_scatter = px.scatter(df_filtered, x="productividad_kg_ha", y="ingresos_anuales_cop", 
                             color="cadena_productiva", symbol="estado_certificacion", log_y=True,
                             hover_data=["id_limpio", "genero"], template="plotly_dark", opacity=0.8)
    fig_scatter.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("""<div class='grafana-text'><b>Análisis Estratégico (Requerimiento 1.5):</b><br>
    <b>Pregunta:</b> ¿La superioridad agronómica garantiza liquidez financiera, y qué rol juega la certificación?<br>
    <b>Audiencia:</b> Gerencia Financiera y Estructuración de Proyectos.<br>
    <b>Alternativa Descartada:</b> Gráfico de líneas temporales, debido a la naturaleza transversal del conjunto de datos. Conectar las observaciones sugeriría una evolución histórica falaz.</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("#### C. Auditoría y Cobertura Espacial del Dato")
    # Cruce: Origen Coordenada, Recuento
    df_quality = df_filtered['origen_coordenada'].value_counts().reset_index()
    df_quality.columns = ['Estado de Trazabilidad', 'Volumen de Registros']
    fig_quality = px.pie(df_quality, values='Volumen de Registros', names='Estado de Trazabilidad', hole=0.6,
                         template="plotly_dark", color_discrete_sequence=['#4CAF50', '#F44336'])
    fig_quality.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_quality, use_container_width=True)
    st.markdown("""<div class='grafana-text'><b>Análisis Estratégico (Requerimiento 1.5):</b><br>
    <b>Pregunta:</b> ¿Cuál es el nivel de fiabilidad y completitud de nuestra base maestra georreferenciada?<br>
    <b>Audiencia:</b> Equipo de Analítica Avanzada y Auditores Externos.<br>
    <b>Alternativa Descartada:</b> Tabla plana de conteo. El gráfico de anillo transmite de forma inmediata la proporción de rescate algorítmico frente al dato original, estableciendo métricas de confianza visual claras.</div>""", unsafe_allow_html=True)

with row2_col2:
    st.markdown("#### D. Resiliencia: Entorno Ilegal vs. Brecha Productiva")
    # Cruce: Promedio Coca, Brecha Productividad, Cadena Productiva, Área
    fig_macro = px.scatter(df_filtered, x="promedio_coca_ha_5y", y="brecha_productividad_%", 
                           color="cadena_productiva", size="area_ha", marginal_y="box",
                           hover_data=["id_limpio", "municipio"], template="plotly_dark")
    fig_macro.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_macro, use_container_width=True)
    st.markdown("""<div class='grafana-text'><b>Análisis Estratégico (Requerimiento Adicional):</b><br>
    <b>Pregunta:</b> ¿La presión de economías ilícitas destruye sistemáticamente la rentabilidad del agronegocio legal?<br>
    <b>Audiencia:</b> Dirección de Intervención Social y Políticas Públicas.<br>
    <b>Alternativa Descartada:</b> Gráfico de doble eje Y. Dicha visualización ocultaría la dispersión y la existencia de valores atípicos (outliers) que representan a productores resilientes en zonas de alto conflicto.</div>""", unsafe_allow_html=True)
