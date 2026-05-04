import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. CONFIGURACIÓN DE INTERFAZ CORPORATIVA (ESTILO CYBERPUNK / NEON)
st.set_page_config(page_title="Inteligencia Territorial", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    header[data-testid="stHeader"] { visibility: hidden; display: none; }
    
    /* Fondo morado profundo de la aplicación */
    .stApp { background-color: #0d0614; font-family: 'Segoe UI', Tahoma, sans-serif; }
    
    /* Panel lateral con un tono ligeramente distinto */
    [data-testid="stSidebar"] { background-color: #130a1f !important; border-right: 1px solid #2a1642; }
    [data-testid="stSidebar"] * { color: #e0d4f5 !important; }
    
    /* Filtros fondo oscuro morado */
    div[data-baseweb="select"] > div { background-color: #1a0d2b !important; border: 1px solid #3d2063 !important; color: #ffffff !important; }
    ul[data-baseweb="menu"] { background-color: #1a0d2b !important; }
    ul[data-baseweb="menu"] li { color: #ffffff !important; }
    span[data-baseweb="tag"] { background-color: #00e5ff !important; color: #000000 !important; font-weight: bold;}
    
    /* Títulos y textos */
    h1, h2, h3, h4 { color: #ffffff !important; font-weight: 500; font-size: 1.1rem; margin-bottom: 0px; }
    p, label { color: #bbaacc !important; }
    
    /* Tarjetas de Indicadores (KPIs) estilo Neon */
    div[data-testid="metric-container"] { 
        background-color: #170a29; 
        border-top: 3px solid #b400ff; 
        padding: 15px 15px; 
        border-radius: 8px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetricLabel"] { 
        font-size: 0.80rem !important; 
        color: #bbaacc !important; 
        white-space: normal !important; 
        margin-bottom: 5px; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
        line-height: 1.2 !important;
    }
    div[data-testid="stMetricValue"] > div { 
        color: #00e5ff !important; 
        font-size: 1.5rem !important; 
        font-weight: bold;
    }
    
    .reportview-container .main .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    .grafica-explicacion { font-size: 0.75rem; color: #887799; text-align: justify; margin-top: 5px; line-height: 1.2;}
</style>
""", unsafe_allow_html=True)

st.title("Productores Aliados Solidaridad Colombia")
st.markdown("Monitoreo de indicadores agronómicos, evaluación de riesgo climático y exposición a economías ilícitas.")
st.markdown("---")

# 2. CARGA Y PREPARACIÓN DE DATOS
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
    
    if 'edad' in df.columns:
        bins = [0, 35, 55, 120]
        labels = ['Joven (<35)', 'Adulto (35-55)', 'Mayor (>55)']
        df['categoria_edad'] = pd.cut(df['edad'], bins=bins, labels=labels, right=False)
        
    return df

df = load_data()

# 3. PANEL LATERAL DE SEGMENTACIÓN
st.sidebar.markdown("### Filtros de Análisis")
depto_sel = st.sidebar.multiselect("Departamento", options=sorted(df['departamento'].dropna().unique()))
muni_options = sorted(df[df['departamento'].isin(depto_sel)]['municipio'].dropna().unique()) if depto_sel else sorted(df['municipio'].dropna().unique())
muni_sel = st.sidebar.multiselect("Municipio", options=muni_options)
cadena_sel = st.sidebar.multiselect("Cadena Productiva", options=sorted(df['cadena_productiva'].dropna().unique()))
genero_sel = st.sidebar.multiselect("Género", options=sorted(df['genero'].dropna().unique()))
cert_sel = st.sidebar.multiselect("Estado Certificación", options=sorted(df['estado_certificacion'].dropna().astype(str).unique()))
vuln_sel = st.sidebar.multiselect("Vulnerabilidad Cambio Climático", options=sorted(df['Vulnerabilidad CC'].dropna().unique()))

df_filtered = df.copy()
if depto_sel: df_filtered = df_filtered[df_filtered['departamento'].isin(depto_sel)]
if muni_sel: df_filtered = df_filtered[df_filtered['municipio'].isin(muni_sel)]
if cadena_sel: df_filtered = df_filtered[df_filtered['cadena_productiva'].isin(cadena_sel)]
if genero_sel: df_filtered = df_filtered[df_filtered['genero'].isin(genero_sel)]
if cert_sel: df_filtered = df_filtered[df_filtered['estado_certificacion'].isin(cert_sel)]
if vuln_sel: df_filtered = df_filtered[df_filtered['Vulnerabilidad CC'].isin(vuln_sel)]

# 4. INDICADORES MACRO (KPIs)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total de Productores", f"{len(df_filtered):,}")
k2.metric("Superficie Total (Ha)", f"{df_filtered['area_ha'].sum():,.1f}")
k3.metric("Producción (Kg)", f"{df_filtered['produccion_kg'].sum():,.0f}")
k4.metric("Brecha Productividad", f"{df_filtered['brecha_productividad_%'].mean():.1f}%")
vcr_mean = df_filtered['VCR'].mean() if 'VCR' in df_filtered.columns else 0.0
k5.metric("Índice Ventaja Comparativa", f"{vcr_mean:.2f}")
horas_promedio = df_filtered['horas_capacitacion_2024'].mean() if 'horas_capacitacion_2024' in df_filtered.columns else 0
k6.metric("Promedio Capacitación", f"{horas_promedio:.1f} Hrs")

st.markdown("<br>", unsafe_allow_html=True)

# 5. CONFIGURACIÓN GLOBAL DE GRÁFICAS
layout_config = dict(
    paper_bgcolor='#170a29', 
    plot_bgcolor='#170a29',  
    font=dict(color="#d4c5e8", size=11), 
    margin=dict(l=15, r=15, t=40, b=120), 
    xaxis=dict(showgrid=False, zeroline=False, color='#bbaacc', title_font=dict(color='#d4c5e8')), 
    yaxis=dict(showgrid=False, zeroline=False, color='#bbaacc', title_font=dict(color='#d4c5e8')), 
    legend=dict(font=dict(color="#d4c5e8"), title_font=dict(color="#d4c5e8"), orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5) 
)

nombres_ejes = {
    "productividad_kg_ha": "Productividad (Pnd kg / Area ha)",
    "ingresos_anuales_cop": "Ingresos Anuales (COP)",
    "promedio_coca_ha_5y": "Exposición a Cultivos Ilícitos (Ha)",
    "brecha_productividad_%": "Brecha de Productividad (%)",
    "año_cosecha": "Año de Cosecha",
    "Cantidad": "Número de Productores",
    "Volumen": "Total de Productores",
    "categoria_edad": "Grupo Etario",
    "horas_capacitacion_2024": "Promedio de Horas de Capacitación",
    "año_ingreso_programa": "Año de Ingreso al Programa",
    "cadena_productiva": "Cadena Productiva",
    "estado_certificacion": "Estado de Certificación",
    "genero": "Género",
    "Vulnerabilidad CC": "Vulnerabilidad Cambio Climático"
}

# PALETAS DE COLORES NEÓN
color_cadena = ['#00e5ff', '#ff007f', '#39ff14', '#ff8c00', '#b400ff']
color_cert = ['#00e5ff', '#39ff14', '#ff007f'] 
color_edad = ['#b400ff', '#00e5ff', '#ff8c00'] 
color_genero = ['#ff007f', '#00e5ff'] 

# ==========================================
# 6. PRIMERA FILA: GRÁFICAS 
# ==========================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("#### Análisis Territorial Nacional")
    fig_map = px.scatter_mapbox(df_filtered, lat="latitud", lon="longitud", color="Vulnerabilidad CC", 
                                size="produccion_kg", hover_name="municipio", 
                                hover_data={"Vulnerabilidad CC": True, "produccion_kg": True, "latitud": False, "longitud": False},
                                mapbox_style="open-street-map",
                                zoom=3.5, center={"lat": 4.0, "lon": -73.5},
                                labels=nombres_ejes, color_discrete_sequence=color_cadena)
    fig_map.update_layout(**layout_config)
    fig_map.update_layout(showlegend=True, height=480, margin=dict(l=0, r=0, t=0, b=120), legend_title_text="")
    st.plotly_chart(fig_map, use_container_width=True)

with c2:
    st.markdown("#### Ingresos vs Productividad")
    # TEXTO ELIMINADO PARA LIMPIAR LA GRÁFICA
    fig_scatter = px.scatter(df_filtered, x="productividad_kg_ha", y="ingresos_anuales_cop", 
                             color="cadena_productiva", log_y=True,
                             color_discrete_sequence=color_cadena, labels=nombres_ejes)
    fig_scatter.update_layout(**layout_config)
    fig_scatter.update_layout(showlegend=True, height=480, legend_title_text="")
    fig_scatter.update_traces(marker=dict(size=7, opacity=0.8, line=dict(width=1, color='White')))
    st.plotly_chart(fig_scatter, use_container_width=True)

with c3:
    st.markdown("#### Estado de Certificación")
    df_cert = df_filtered['estado_certificacion'].value_counts().reset_index()
    df_cert.columns = ['Estado', 'Volumen']
    fig_cert = px.pie(df_cert, values='Volumen', names='Estado', hole=0.6, 
                      color_discrete_sequence=color_cert, labels=nombres_ejes)
    fig_cert.update_traces(textposition='inside', textinfo='percent+label', showlegend=False, marker=dict(line=dict(color='#170a29', width=2)))
    fig_cert.update_layout(**layout_config)
    fig_cert.update_layout(height=480, showlegend=False)
    st.plotly_chart(fig_cert, use_container_width=True)

with c4:
    st.markdown("#### Exposición a cultivos vs Brecha")
    # TEXTO ELIMINADO PARA LIMPIAR LA GRÁFICA
    fig_macro = px.scatter(df_filtered, x="promedio_coca_ha_5y", y="brecha_productividad_%", 
                           color="cadena_productiva", size="area_ha",
                           color_discrete_sequence=color_cadena, labels=nombres_ejes)
    fig_macro.update_layout(**layout_config)
    fig_macro.update_layout(showlegend=True, height=480, legend_title_text="")
    fig_macro.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='White')))
    st.plotly_chart(fig_macro, use_container_width=True)

# ==========================================
# 7. PRIMERA FILA: TEXTOS EXPLICATIVOS
# ==========================================
t1, t2, t3, t4 = st.columns(4)
with t1: st.markdown("<div class='grafica-explicacion'>Visualiza la distribución geográfica de los productores junto con su nivel de vulnerabilidad climática. El tamaño de cada burbuja representa el volumen de producción, facilitando identificar las zonas donde se concentra la mayor parte de la producción del país y el nivel de riesgo ambiental al que están expuestos esos cultivos clave..</div>", unsafe_allow_html=True)
with t2: st.markdown("<div class='grafica-explicacion'>Compara rendimiento físico frente al retorno financiero anual (escala logarítmica).</div>", unsafe_allow_html=True)
with t3: st.markdown("<div class='grafica-explicacion'>Proporción de productores según su estado actual de certificación.</div>", unsafe_allow_html=True)
with t4: st.markdown("<div class='grafica-explicacion'>Cruza la exposición a cultivos ilícitos (eje X) con la eficiencia agronómica (eje Y).</div>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 8. SEGUNDA FILA: GRÁFICAS 
# ==========================================
c5, c6, c7, c8 = st.columns(4)

with c5:
    st.markdown("#### Cosecha/Certificación")
    df_cosecha = df_filtered.groupby(['año_cosecha', 'estado_certificacion']).size().reset_index(name='Cantidad')
    fig_cosecha = px.bar(df_cosecha, x='año_cosecha', y='Cantidad', color='estado_certificacion', 
                         text='Cantidad', barmode='group', color_discrete_sequence=color_cert, labels=nombres_ejes)
    fig_cosecha.update_layout(**layout_config)
    fig_cosecha.update_layout(height=480, legend_title_text="")
    fig_cosecha.update_traces(textposition='outside', textangle=0, cliponaxis=False, textfont=dict(color="#ffffff"))
    st.plotly_chart(fig_cosecha, use_container_width=True)

with c6:
    st.markdown("#### Capacitación vs Edad")
    df_edad_cap = df_filtered.groupby('categoria_edad', observed=False)['horas_capacitacion_2024'].mean().reset_index()
    fig_edad = px.bar(df_edad_cap, x='categoria_edad', y='horas_capacitacion_2024', 
                      text='horas_capacitacion_2024', color='categoria_edad', 
                      color_discrete_sequence=color_edad, labels=nombres_ejes)
    fig_edad.update_layout(**layout_config, showlegend=False, height=480)
    fig_edad.update_traces(texttemplate='%{text:.1f}', textposition='outside', textangle=0, cliponaxis=False, textfont=dict(color="#ffffff"))
    st.plotly_chart(fig_edad, use_container_width=True)

with c7:
    st.markdown("#### Ingreso al Programa")
    df_ingreso = df_filtered.groupby('año_ingreso_programa').size().reset_index(name='Volumen')
    fig_ingreso = px.area(df_ingreso, x='año_ingreso_programa', y='Volumen', text='Volumen', labels=nombres_ejes)
    fig_ingreso.update_layout(**layout_config)
    fig_ingreso.update_layout(height=480)
    fig_ingreso.update_xaxes(type='category')
    fig_ingreso.update_traces(line_shape='spline', textposition="top center", 
                              line=dict(color='#ff007f', width=4), fillcolor='rgba(255, 0, 127, 0.15)',
                              marker=dict(size=8, color="#ffffff"), textfont=dict(color="#ffffff"))
    st.plotly_chart(fig_ingreso, use_container_width=True)

with c8:
    st.markdown("#### Equidad por Cadena")
    df_genero = df_filtered.groupby(['cadena_productiva', 'genero']).size().reset_index(name='Cantidad')
    fig_genero = px.bar(df_genero, x='cadena_productiva', y='Cantidad', color='genero',
                        text='Cantidad', barmode='group', color_discrete_sequence=color_genero, labels=nombres_ejes)
    fig_genero.update_layout(**layout_config)
    fig_genero.update_layout(height=480, legend_title_text="")
    fig_genero.update_traces(textposition='outside', textangle=0, cliponaxis=False, textfont=dict(color="#ffffff"))
    st.plotly_chart(fig_genero, use_container_width=True)

# ==========================================
# 9. SEGUNDA FILA: TEXTOS EXPLICATIVOS
# ==========================================
t5, t6, t7, t8 = st.columns(4)
with t5: st.markdown("<div class='grafica-explicacion'>Distribución de productores según año de cosecha y estatus de certificación.</div>", unsafe_allow_html=True)
with t6: st.markdown("<div class='grafica-explicacion'>Promedio de horas de capacitación recibidas segmentado por rango etario.</div>", unsafe_allow_html=True)
with t7: st.markdown("<div class='grafica-explicacion'>Evolución histórica del volumen de productores adheridos al programa.</div>", unsafe_allow_html=True)
with t8: st.markdown("<div class='grafica-explicacion'>Análisis de participación por sexo dentro de cada cadena productiva.</div>", unsafe_allow_html=True)

st.markdown("---")

# 10. MATRIZ DE DATOS COMPACTA
st.markdown("#### Matriz Transaccional de Productores")
st.dataframe(df_filtered[['id_limpio', 'departamento', 'municipio', 'cadena_productiva', 'genero', 'categoria_edad', 'estado_certificacion', 'Vulnerabilidad CC', 'brecha_productividad_%', 'ingresos_anuales_cop']], height=200, use_container_width=True)
