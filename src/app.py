import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go


path = r"C:\Users\rgramos\pos_mineracao\dashboard\src\data\dados_completos_es.geojson"
path_gpkg = r"C:\Users\rgramos\pos_mineracao\dashboard\src\data\dados_completos_es.gpkg"

st.markdown("""
<div style='text-align: center; font-size: 25px;  font-weight: bold; margin-bottom: 1rem'>
📊 Painel de Desempenho Escolar
</div>
""", unsafe_allow_html=True)

# Tratamento dos dados
dependence = {
     1: "Federal",
     2: "Estadual",
     3: "Municipal",
     4: "Privada",
}

localization = {
     1: "Urbana",
     2: "Rural"
}

features = [
    "nm_mun",
    "cd_rgi",
    "area_km2",
    "ano",
    "dependencia_id",
    "localizacao_id",
    "serie_id",
    "perc_aprovados",
    "perc_reprovados",
    "perc_abandono",
    "geometry",
    "sre"
]

st.set_page_config(layout="wide")

@st.cache_data
def open_df(path):
    return gpd.read_file(path)


@st.cache_data
def simplify_df(_df):
    df_copy = _df.copy()
    df_copy['geometry'] = df_copy['geometry'].simplify(tolerance=0.01, preserve_topology=True)
    return df_copy

df = open_df(path_gpkg)
df = simplify_df(df)

total_schools = df.shape[0]
total_cities = df['nm_mun'].nunique()

df["dependencia_nome"] = df["dependencia_id"].map(dependence)
df['localizacao_nome'] = df['localizacao_id'].map(localization)
df["geometry"] = df["geometry"].simplify(tolerance=0.005, preserve_topology=True)


results_df = df[['nm_mun','perc_aprovados', 'perc_reprovados', 'perc_abandono', 'geometry', 'sre']]


df_filtered_per_mun = df.groupby('nm_mun')[['perc_aprovados', 'perc_reprovados', 'perc_abandono']].mean().reset_index().set_index("nm_mun")
means_df_per_sre = df.groupby('sre')[['perc_aprovados', 'perc_reprovados', 'perc_abandono']].mean()

mean_approveds_per_mun = df.groupby("nm_mun")["perc_aprovados"].mean().reset_index().set_index("nm_mun")
mean_approveds_per_dependece = df.groupby("dependencia_nome")["perc_aprovados"].mean().reset_index().set_index("dependencia_nome")
mean_approveds_per_localization = df.groupby("localizacao_nome")["perc_aprovados"].mean().reset_index().set_index("localizacao_nome")

mean_reproved_per_mun = df.groupby("nm_mun")["perc_reprovados"].mean().reset_index().set_index("nm_mun")
mean_reproved_per_dependence = df.groupby("dependencia_nome")["perc_reprovados"].mean().reset_index().set_index("dependencia_nome")
mean_reproved_per_localization = df.groupby("localizacao_nome")["perc_reprovados"].mean().reset_index().set_index("localizacao_nome")

mean_dropout_per_mun = df.groupby("nm_mun")["perc_abandono"].mean().reset_index().set_index("nm_mun")
mean_dropout_per_dependence = df.groupby("dependencia_nome")["perc_abandono"].mean().reset_index().set_index("dependencia_nome")
mean_dropout_per_localization = df.groupby("localizacao_nome")["perc_abandono"].mean().reset_index().set_index("localizacao_nome")



# Mapear os DataFrames por aba e tipo de indicador
data_sources = {
    "Por município": {
        "Percentual de Aprovação": mean_approveds_per_mun,
        "Percentual de reprovação": mean_reproved_per_mun,
        "Percentual de Abandono": mean_dropout_per_mun
    },
    "Por dependência": {
        "Percentual de Aprovação": mean_approveds_per_dependece,
        "Percentual de reprovação": mean_reproved_per_dependence,
        "Percentual de Abandono": mean_dropout_per_dependence
    },
    "Por localização": {
        "Percentual de Aprovação": mean_approveds_per_localization,
        "Percentual de reprovação": mean_reproved_per_localization,
        "Percentual de Abandono": mean_dropout_per_localization
    }
}

# Gráfico de barras Superintendências
with st.container():
    col1, col2 = st.columns([3,1])
    with col1:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>Superintendências</h4>", unsafe_allow_html=True)
            st.bar_chart(means_df_per_sre)
    with col2:
         with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>Total de Escolas</h4>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center; font-weight: bold;'>{total_schools}</h2>", unsafe_allow_html=True)
         
         with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>Total de Municípios</h4>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center; font-weight: bold;'>{total_cities}</h2>", unsafe_allow_html=True)
 
       


# Função genérica prara gerar gráfico de barras
def handle_plot_bar_chart(tab_name, tab):
    with tab:
        st.subheader(f"Gráfico - {tab_name}")
        df = data_sources.get(tab_name, {}).get(option)
        if df is not None:
            st.bar_chart(df, use_container_width=True)
        else:
            st.warning("Dados não disponíveis para esta combinação.")

with st.container():
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.text("")
    with col2:
        option = st.selectbox(
                    " ",
                    ['Percentual de Aprovação', 'Percentual de reprovação', 'Percentual de Abandono'],
                    index=0,
                    accept_new_options=True,
                    )
    with col3:
        st.text("")

tab1, tab2, tab3 = st.tabs(['Por município', 'Por dependência', 'Por localização'])
handle_plot_bar_chart("Por município", tab1)
handle_plot_bar_chart("Por dependência", tab2)
handle_plot_bar_chart("Por localização", tab3)


        

# Mapa interativo utilizando Folium
def generate_colors(n):
    cmap = plt.get_cmap('tab10')
    return [mcolors.rgb2hex(cmap(i % 10)) for i in range(n)]

def plot_gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 12}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'bgcolor': "white",
        }
    ))

    fig.update_layout(
        height=140,  # Altura reduzida
        width=220,   # Largura mais compacta
        margin=dict(t=40, b=10, l=10, r=10)
    )

    return fig




def generate_folium_map(gdf, selected_sre=None):
    m = folium.Map(location=[-19.5, -40.7], zoom_start=7, tiles='cartodbpositron')
    
    def style_function(feature):
        sre_name = feature['properties']['sre']
        is_selected = sre_name == selected_sre
        color = '#ff0000' if is_selected else '#3186cc'
        return {
            'fillColor': color,
            'color': 'black',
            'weight': 3 if is_selected else 1,
            'fillOpacity': 0.9 if is_selected else 0.6,
        }

    folium.GeoJson(
        gdf,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=["sre", "nm_mun"], aliases=["SRE", "Município"])
    ).add_to(m)

    return m

# === Interface ===

# st.subheader("Painel das SREs")

st.markdown("<h4 style='text-align: center; font-size: 25px;' >Painel das SRE's</h4>", unsafe_allow_html=True)

# Sidebar ou topo centralizado com filtro
with st.container():
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.text("")
    with col2:    
        selected_sre = st.selectbox("Selecione a SRE:", options=results_df['sre'].unique())
    with col3:
        st.text("")


# Dados da SRE
@st.cache_data
def calcule_means_for_sre(results_df, selected_sre):
    sre_filtered = results_df[results_df['sre'] == selected_sre]
    media_aprov = sre_filtered['perc_aprovados'].mean()
    media_reprov = sre_filtered['perc_reprovados'].mean()
    media_aband = sre_filtered['perc_abandono'].mean()
    return media_aprov, media_reprov, media_aband

results_without_geom = results_df.drop(columns=['geometry']).copy()
media_aprov, media_reprov, media_aband = calcule_means_for_sre(results_without_geom, selected_sre)

# Layout com mapa e indicadores
with st.container():
    col1, col2 = st.columns([3, 1])

    with col1:
        m = generate_folium_map(results_df, selected_sre)
        st_folium(m, width=700, height=500)

    with col2:
        st.plotly_chart(plot_gauge("Aprovados (%)", media_aprov, "green"), use_container_width=True)
        st.plotly_chart(plot_gauge("Reprovados (%)", media_reprov, "orange"), use_container_width=True)
        st.plotly_chart(plot_gauge("Abandono (%)", media_aband, "red"), use_container_width=True)
        











    
        






     

































# st.dataframe(df.head())




