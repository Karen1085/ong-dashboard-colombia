import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página (Ancho completo y Modo Oscuro por defecto)
st.set_page_config(page_title="Dashboard Estratégico ONG", layout="wide")

st.title("🚀 Sistema de Inteligencia Territorial - ONG")
st.markdown("Análisis avanzado de productividad, riesgo climático y econometría espacial.")

# 1. CARGA DE DATOS
@st.cache_data # Para que la app sea veloz
def load_data():
    return pd.read_excel("Base_Maestra_ONG_PowerBI.xlsx")

df = load_data()

# 2. BARRA LATERAL (FILTROS GLOBALES INTERACTIVOS)
st.sidebar.header("🎯 Filtros de Control")
depto_sel = st.sidebar.multiselect("Selecciona Departamento", options=sorted(df['departamento'].unique()), default=[])
muni_sel = st.sidebar.multiselect("Selecciona Municipio", options=sorted(df[df['departamento'].isin(depto_sel)]['municipio'].unique()) if depto_sel else sorted(df['municipio'].unique()))
cadena_sel = st.sidebar.multiselect("Cadena Productiva", options=sorted(df['cadena_productiva'].unique()))

# Lógica de filtrado
df_filtrado = df.copy()
if depto_sel: df_filtrado = df_filtrado[df_filtrado['departamento'].isin(depto_sel)]
if muni_sel: df_filtrado = df_filtrado[df_filtrado['municipio'].isin(muni_sel)]
if cadena_sel: df_filtrado = df_filtrado[df_filtrado['cadena_productiva'].isin(cadena_sel)]

# 3. KPIs (Métricas principales)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Productores", f"{len(df_filtrado)}")
col2.metric("Hectáreas Totales", f"{df_filtrado['area_ha'].sum():,.1f}")
col3.metric("Brecha Media", f"{df_filtrado['brecha_productividad_%'].mean():.2f}%")
col4.metric("Ingreso Anual (Prom)", f"${df_filtrado['ingresos_anuales_cop'].mean():,.0f}")

# 4. DASHBOARD (Gráficos en 2 columnas)
c1, c2 = st.columns(2)

with c1:
    st.subheader("📍 Mapa de Riesgo y ROI")
    fig_map = px.scatter_mapbox(df_filtrado, lat="latitud", lon="longitud", color="Vulnerabilidad CC", 
                               size="produccion_kg", mapbox_style="carto-positron", zoom=4)
    st.plotly_chart(fig_map, use_container_width=True)

with c2:
    st.subheader("📈 Relación Ingresos vs Productividad")
    fig_scat = px.scatter(df_filtrado, x="productividad_kg_ha", y="ingresos_anuales_cop", 
                         color="cadena_productiva", log_y=True, hover_name="nombre_completo")
    st.plotly_chart(fig_scat, use_container_width=True)

# 5. TABLA DE DATOS DETALLADA (Al final)
st.subheader("📋 Detalle de Productores Filtrados")
st.dataframe(df_filtrado[['nombre_completo', 'municipio', 'cadena_productiva', 'brecha_productividad_%', 'VCR']])
