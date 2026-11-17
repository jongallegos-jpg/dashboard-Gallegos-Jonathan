import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIGURACIÓN =================
ARCHIVO     = 'datos_limpios (2).csv'
TITULO      = 'Propiedades RM | Insights & Valoración'
DESCRIPCION = 'Análisis interactivo de precios y superficies de viviendas en la Región Metropolitana.'
AUTOR       = 'Jonathan Gallegos'
KAGGLE      = 'https://www.kaggle.com/datasets/...'

COL_CAT  = 'Comuna'
COL_NUM  = 'Price_CLP'
COL_NUM2 = 'Total Area'
# =================================================

# Configuración de página profesional
st.set_page_config(
    page_title=TITULO,
    page_icon='🏠',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Estilo CSS personalizado para mejorar la estética general
st.markdown("""
    <style>
    .main {
        background-color: #f9fbfd;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: bold;
        color: #1e3d59;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #17b978;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    return pd.read_csv(ARCHIVO)

df = cargar_datos()

# Encabezado Principal estilizado
st.title(f'🏠 {TITULO}')
st.caption(f'**Desarrollado por:** {AUTOR} | **Fuente:** [Kaggle Dataset]({KAGGLE})')
st.markdown(f'*{DESCRIPCION}*')
st.markdown('---')

# ---------- BARRA LATERAL (Filtros Colapsables) ----------
st.sidebar.image('https://img.icons8.com/fluency/96/home.png', width=80)
st.sidebar.header('Filtros Avanzados')

categorias = sorted(df[COL_CAT].dropna().astype(str).unique())
sel_cat = st.sidebar.multiselect(f'📍 Seleccionar {COL_CAT} (Vacío = Todas)', categorias)

minimo = float(df[COL_NUM].min())
maximo = float(df[COL_NUM].max())
# Presentar el slider con formato legible
rango = st.sidebar.slider(
    f'💰 Rango de Precio ({COL_NUM})',
    minimo, maximo, (minimo, maximo),
    format="$%,.0f"
)

# Aplicar Filtros
df_f = df[df[COL_NUM].between(rango[0], rango[1])]
if sel_cat:
    df_f = df_f[df_f[COL_CAT].astype(str).isin(sel_cat)]

if df_f.empty:
    st.warning('⚠️ No se encontraron registros para los filtros seleccionados.')
    st.stop()

# ---------- INDICADORES (KPIs en Tarjetas) ----------
with st.container():
    k1, k2, k3, k4 = st.columns(4)
    
    # Registros
    k1.metric(
        label='📂 Propiedades Filtradas',
        value=f'{len(df_f):,}',
        delta=f'{len(df_f) / len(df) * 100:.1f}% del total',
        delta_color='normal'
    )
    
    # Promedio en CLP
    promedio_actual = df_f[COL_NUM].mean()
    diff_total = promedio_actual - df[COL_NUM].mean()
    k2.metric(
        label=f'💵 Precio Promedio',
        value=f'$ {promedio_actual:,.0f}',
        delta=f'$ {diff_total:+,.0f} vs. total',
        delta_color='inverse'
    )
    
    # Mediana en CLP
    k3.metric(
        label=f'📊 Precio Mediano',
        value=f'$ {df_f[COL_NUM].median():,.0f}'
    )
    
    # Comuna más destacada
    comuna_top = str(df_f[COL_CAT].mode()[0])
    k4.metric(
        label='📍 Comuna Predominante',
        value=comuna_top
    )

st.markdown('---')

# ---------- SECCIÓN DE GRÁFICOS CON PALETAS PROFESIONALES ----------
color_theme = px.colors.sequential.Tealgrn # Paleta elegante verde-azulada

top10 = df_f[COL_CAT].value_counts().head(10).index
df_top = df_f[df_f[COL_CAT].isin(top10)]

fila1_izq, fila1_der = st.columns(2)

with fila1_izq:
    conteo = df_top[COL_CAT].value_counts().reset_index()
    conteo.columns = [COL_CAT, 'cantidad']
    fig1 = px.bar(conteo, x='cantidad', y=COL_CAT, orientation='h',
                  title=f'🔝 Top 10 Comunas por Cantidad de Ofertas',
                  labels={'cantidad': 'Número de Propiedades', COL_CAT: 'Comuna'},
                  color='cantidad', color_continuous_scale=color_theme)
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig1, use_container_width=True)

with fila1_der:
    fig2 = px.histogram(df_f, x=COL_NUM, nbins=40,
                        title=f'📈 Distribución de Precios de Venta',
                        labels={COL_NUM: 'Precio (CLP)'},
                        color_discrete_sequence=['#17b978'])
    fig2.update_layout(yaxis_title='Frecuencia', margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig2, use_container_width=True)

fila2_izq, fila2_der = st.columns(2)

with fila2_izq:
    fig3 = px.box(df_top, x=COL_CAT, y=COL_NUM,
                  title=f'📦 Dispersión de Precios por Comuna (Top 10)',
                  color=COL_CAT, color_discrete_sequence=px.colors.qualitative.Safe)
    fig3.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig3, use_container_width=True)

with fila2_der:
    muestra = df_f.sample(min(len(df_f), 2000), random_state=42)
    r = df_f[COL_NUM].corr(df_f[COL_NUM2])
    fig4 = px.scatter(muestra, x=COL_NUM2, y=COL_NUM, opacity=0.4, size_max=10,
                      title=f'📐 Relación Superficie vs Precio (r = {r:.2f})',
                      labels={COL_NUM2: 'Área Total (m²)', COL_NUM: 'Precio (CLP)'},
                      color_discrete_sequence=['#1e3d59'])
    fig4.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig4, use_container_width=True)

# ---------- TREEMAP HIGHLIGHT ----------
st.subheader('📊 Distribución Proporcional del Mercado')
fig5 = px.treemap(conteo, path=[px.Constant('RM'), COL_CAT],
                  values='cantidad',
                  title=f'Proporción Visual de Registros por {COL_CAT}',
                  color='cantidad', color_continuous_scale=color_theme)
fig5.update_traces(textinfo='label+percent entry')
st.plotly_chart(fig5, use_container_width=True)

# ---------- EXPLORADOR DE DATOS ----------
with st.expander('🔍 Explorar tabla de datos filtrados'):
    st.dataframe(df_f, use_container_width=True)
    
    st.download_button(
        label='⬇️ Descargar esta selección como CSV',
        data=df_f.to_csv(index=False).encode('utf-8'),
        file_name='propiedades_filtradas.csv',
        mime='text/csv'
    )

# ---------- CONCLUSIONES DINÁMICAS ----------
st.subheader('💡 Insights y Conclusiones del Análisis')

promedio_clp = df_f[COL_NUM].mean()
comuna_moda = df_f[COL_CAT].mode()[0]

st.markdown(f"""
- **Mayor concentración de mercado:** La comuna con mayor volumen de propiedades disponibles bajo los filtros seleccionados es **{comuna_moda}**.
- **Ticket Promedio:** El valor promedio de las viviendas bajo el rango establecido se ubica en **$ {promedio_clp:,.0f} CLP**.
- **Correlación Área-Precio:** El coeficiente de correlación de Pearson es de **{r:.2f}**, lo que describe el impacto del tamaño de las propiedades sobre su valor final de mercado.
""")
