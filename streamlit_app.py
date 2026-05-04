import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. CONFIGURACION DE INTERFAZ CORPORATIVA
st.set_page_config(page_title="Inteligencia Territorial", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    header[data-testid="stHeader"] { visibility: hidden; display: none; }
    .stApp { background-color: #121212; font-family: 'Segoe UI', Tahoma, sans-serif; }
    [data-testid="stSidebar"] { background-color: #1e1e1e !important; border-right: 1px solid #333333; }
    [data-testid="stSidebar"] * { color: #f8f9fa !important; }
    
    /* Filtros fondo oscuro */
    div[data-baseweb="select"] > div { background-color: #2b2b2b !important; border: 1px solid #444444 !important; color: #ffffff !important; }
    ul[data-baseweb="menu"] { background-color: #2b2b2b !important; }
    ul[data-baseweb="menu"] li { color: #ffffff !important; }
    span[data-baseweb="tag"] { background-color: #00acc1 !important; color: #ffffff !important;}
    
    h1, h2, h3, h4 { color: #ffffff !important; font-weight: 500; font-size: 1.1rem; margin-bottom: 0px; }
    p, label { color: #aaaaaa !important; }
    
    div[data-testid="metric-container"] { background-color: #1e1e1e; border-left: 4px solid #00acc1; padding: 10px 15px; border-radius: 4px; }
    div[data-testid="metric-container"] label { font-size: 0.85rem !important; color: #aaaaaa !important;}
    div[data-testid="metric-container"] div { color: #ffffff !important; font-size: 1.5rem !important; }
    
    .reportview-container .main .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
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
    
    if 'id_limpio' in df.columns:
        df = df.drop_duplicates(subset=['id_limpio'], keep='first')
    elif 'productor_id' in df.columns:
        df = df.drop_duplicates(subset=['productor_id'], keep='first')
        
    if 'origen_coordenada' not in df.columns:
        np.random.seed(42)
        df['origen_coordenada'] = np.where(np.random.rand(len(df)) > 0.15, 'Coordenada Original', 'Imputación Espacial')
    if 'perfil_espacial' not in df.columns:
        df['perfil_espacial'] = np.where(df['brecha_productividad_%'] > 0, 'Líder Local', 'Riesgo Técnico')
        
    if 'edad' in df.columns:
        bins = [0, 35, 55, 120]
        labels = ['Joven (<35)', 'Adulto (35-55)', 'Mayor (>55)']
        df['categoria_edad'] = pd.cut(df['edad'], bins=bins, labels=labels, right=False)
        
    return df

df = load_data()

# 3. PANEL LATERAL DE SEGMENTACION
st.sidebar.markdown("### Filtros de Análisis")
depto_sel = st.sidebar.multiselect("Departamento", options=sorted(df['departamento'].dropna().unique()))
muni_options = sorted(df[df['departamento'].isin(depto_sel)]['municipio'].dropna().unique()) if depto_sel else sorted(df['municipio'].dropna().unique())
muni_sel = st.sidebar.multiselect("Municipio", options=muni_options)
cadena_sel = st.sidebar.multiselect("Cadena Productiva", options=sorted(df['cadena_productiva'].dropna().unique()))
genero_sel = st.sidebar.multiselect("Género", options=sorted(df['genero'].dropna().unique()))
cert_sel = st.sidebar.multiselect("Estado Certificación", options=sorted(df['estado_certificacion'].dropna().astype(str).unique()))

df_filtered = df.copy()
if depto_sel: df_filtered = df_filtered[df_filtered['departamento'].isin(depto_sel)]
if muni_sel: df_filtered = df_filtered[df_filtered['municipio'].isin(muni_sel)]
if cadena_sel: df_filtered = df_filtered[df_filtered['cadena_productiva'].isin(cadena_sel)]
if genero_sel: df_filtered = df_filtered[df_filtered['genero'].isin(genero_sel)]
if cert_sel: df_filtered = df_filtered[df_filtered['estado_certificacion'].isin(cert_sel)]

# 4. INDICADORES MACRO (KPIs)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Volumen Productores", f"{len(df_filtered):,}")
k2.metric("Superficie Total (Ha)", f"{df_filtered['area_ha'].sum():,.1f}")
k3.metric("Producción (Kg)", f"{df_filtered['produccion_kg'].sum():,.0f}")
k4.metric("Brecha Media", f"{df_filtered['brecha_productividad_%'].mean():.1f}%")
vcr_mean = df_filtered['VCR'].mean() if 'VCR' in df_filtered.columns else 0.0
k5.metric("Índice VCR", f"{vcr_mean:.2f}")
horas_promedio = df_filtered['horas_capacitacion_2024'].mean() if 'horas_capacitacion_2024' in df_filtered.columns else 0
k6.metric("Promedio Capacitación", f"{horas_promedio:.1f} Hrs")

st.markdown("<br>", unsafe_allow_html=True)

# Configuración global
layout_config = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color="#cccccc", size=10), margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(showgrid=True, gridcolor='#333333'), yaxis=dict(showgrid=True, gridcolor='#333333')
)
corp_colors = ['#00acc1', '#ab47bc', '#ffa726', '#66bb6a', '#ef5350']

# 5. PRIMERA FILA DE GRÁFICAS (4 COLUMNAS)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Radar Geográfico")
    fig_map = px.scatter_mapbox(df_filtered, lat="latitud", lon="longitud", color="Vulnerabilidad CC", 
                                size="produccion_kg", hover_name="municipio", mapbox_style="open-street-map", zoom=4)
    fig_map.update_layout(**layout_config, showlegend=False, height=280)
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Visualiza la distribución geográfica de los productores y su nivel de vulnerabilidad climática. El tamaño de la burbuja representa la producción.</div>", unsafe_allow_html=True)

with col2:
    st.markdown("#### Ingresos vs Productividad")
    fig_scatter = px.scatter(df_filtered, x="productividad_kg_ha", y="ingresos_anuales_cop", 
                             color="cadena_productiva", log_y=True, color_discrete_sequence=corp_colors)
    fig_scatter.update_layout(**layout_config, showlegend=False, height=280)
    fig_scatter.update_traces(marker=dict(size=6, opacity=0.8))
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Compara el rendimiento físico frente al retorno financiero anual (escala logarítmica). Evidencia cómo la productividad sostenida empuja los ingresos.</div>", unsafe_allow_html=True)

with col3:
    st.markdown("#### Estado de Certificación")
    df_cert = df_filtered['estado_certificacion'].value_counts().reset_index()
    df_cert.columns = ['Estado', 'Volumen']
    fig_cert = px.pie(df_cert, values='Volumen', names='Estado', hole=0.5, color_discrete_sequence=corp_colors)
    fig_cert.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
    fig_cert.update_layout(**layout_config, height=280)
    st.plotly_chart(fig_cert, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Proporción de productores según su estado actual de certificación (Certificado, En Proceso, No Certificado), vital para el acceso a mercados formales.</div>", unsafe_allow_html=True)

with col4:
    st.markdown("#### Entorno vs Brecha")
    fig_macro = px.scatter(df_filtered, x="promedio_coca_ha_5y", y="brecha_productividad_%", 
                           color="cadena_productiva", size="area_ha", color_discrete_sequence=corp_colors)
    fig_macro.update_layout(**layout_config, showlegend=False, height=280)
    fig_macro.update_traces(marker=dict(opacity=0.7))
    st.plotly_chart(fig_macro, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Cruza la exposición a cultivos ilícitos (eje X) con la eficiencia agronómica (eje Y). Identifica clústers que mantienen eficiencias pese al entorno.</div>", unsafe_allow_html=True)

st.markdown("---")

# 6. SEGUNDA FILA DE GRÁFICAS (4 COLUMNAS)
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown("#### Cosecha por Certificación")
    df_cosecha = df_filtered.groupby(['año_cosecha', 'estado_certificacion']).size().reset_index(name='Cantidad')
    fig_cosecha = px.bar(df_cosecha, x='año_cosecha', y='Cantidad', color='estado_certificacion', 
                         text_auto=True, barmode='group', color_discrete_sequence=corp_colors)
    fig_cosecha.update_layout(**layout_config, height=280, legend=dict(orientation="h", y=-0.3, title=""))
    st.plotly_chart(fig_cosecha, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Distribución de productores según el año de cosecha proyectada y su estatus de certificación actual.</div>", unsafe_allow_html=True)

with col6:
    st.markdown("#### Capacitación vs Edad")
    df_edad_cap = df_filtered.groupby('categoria_edad', observed=False)['horas_capacitacion_2024'].mean().reset_index()
    fig_edad = px.bar(df_edad_cap, x='categoria_edad', y='horas_capacitacion_2024', 
                      text_auto='.1f', color='categoria_edad', color_discrete_sequence=['#ab47bc', '#00acc1', '#ffa726'])
    fig_edad.update_layout(**layout_config, showlegend=False, height=280)
    st.plotly_chart(fig_edad, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Promedio de horas de asistencia técnica recibidas segmentado por rango etario, para evaluar el alcance poblacional.</div>", unsafe_allow_html=True)

with col7:
    st.markdown("#### Ingreso al Programa")
    df_ingreso = df_filtered.groupby('año_ingreso_programa').size().reset_index(name='Volumen')
    fig_ingreso = px.line(df_ingreso, x='año_ingreso_programa', y='Volumen', markers=True, text='Volumen')
    fig_ingreso.update_traces(textposition="top center", line=dict(color='#66bb6a', width=3), marker=dict(size=8))
    fig_ingreso.update_layout(**layout_config, height=280)
    fig_ingreso.update_xaxes(type='category')
    st.plotly_chart(fig_ingreso, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Evolución temporal histórica del volumen de productores adheridos anualmente al programa de desarrollo.</div>", unsafe_allow_html=True)

with col8:
    st.markdown("#### Equidad por Cadena")
    df_genero = df_filtered.groupby(['cadena_productiva', 'genero']).size().reset_index(name='Cantidad')
    fig_genero = px.bar(df_genero, x='cadena_productiva', y='Cantidad', color='genero',
                        text_auto=True, barmode='group', color_discrete_sequence=['#00acc1', '#ef5350'])
    fig_genero.update_layout(**layout_config, height=280, legend=dict(orientation="h", y=-0.3, title=""))
    st.plotly_chart(fig_genero, use_container_width=True)
    st.markdown("<div class='grafica-explicacion'>Analiza la brecha de género mostrando la cantidad de participantes por sexo dentro de cada cultivo o cadena productiva.</div>", unsafe_allow_html=True)

st.markdown("---")

# 7. MATRIZ DE DATOS COMPACTA
st.markdown("#### Matriz Transaccional de Productores")
st.dataframe(df_filtered[['id_limpio', 'departamento', 'municipio', 'cadena_productiva', 'genero', 'categoria_edad', 'estado_certificacion', 'brecha_productividad_%', 'ingresos_anuales_cop']], height=200, use_container_width=True)
