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
<div style='text-align: center; font-size: 20px;  font-weight: bold; margin-bottom: 1rem'>
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


df = open_df(path_gpkg)

df = df[features]

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

total_alunos =300


#Container dos menus
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
 
       





#Parte que controla o gráfico de barras
# Função genérica
def handle_plot_bar_chart(tab_name, tab):
    with tab:
        st.subheader(f"Gráfico - {tab_name}")
        df = data_sources.get(tab_name, {}).get(option)
        if df is not None:
            st.bar_chart(df, use_container_width=True)
        else:
            st.warning("Dados não disponíveis para esta combinação.")
       
option = st.selectbox(
            " ",
            ['Percentual de Aprovação', 'Percentual de reprovação', 'Percentual de Abandono'],
            index=0,
            accept_new_options=True,
            )
tab1, tab2, tab3 = st.tabs(['Por município', 'Por dependência', 'Por localização'])
handle_plot_bar_chart("Por município", tab1)
handle_plot_bar_chart("Por dependência", tab2)
handle_plot_bar_chart("Por localização", tab3)


          

#Plotagem do mapa do ES

# def plot_map(gdf, coluna, titulo, cmap="viridis"):
#     fig, ax = plt.subplots(figsize=(10, 8))
#     gdf.plot(
#         column=coluna,
#         cmap=cmap,
#         legend=True,
#         edgecolor='black',
#         legend_kwds={'label': "Percentual (%)"},
#         ax=ax
#     )
#     ax.set_title(titulo, fontsize=14)
#     ax.axis('off')
#     st.pyplot(fig)


# with st.container():
#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("Visualização no Mapa")
        
#         tab1, tab2, tab3 = st.tabs(['Percentual Aprovados', 'Percentual Reprovados', 'Percentual Abandono'])

#         with tab1:
#             plot_map(gdf=results_df, coluna="perc_aprovados", titulo="Percentual de Aprovados por Município")

#         with tab2:
#             plot_map(gdf=results_df, coluna="perc_reprovados", titulo="Percentual de Reprovados por Município", cmap="OrRd")

#         with tab3:
#             plot_map(gdf=results_df, coluna="perc_abandono", titulo="Percentual de Abandono por Município", cmap="Reds")



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
    unique_sres = gdf['sre'].unique()
    colors = generate_colors(len(unique_sres))
    color_map = dict(zip(unique_sres, colors))

    for idx, row in gdf.iterrows():
        sre_name = row['sre']
        is_selected = (sre_name == selected_sre)

        folium.GeoJson(
            row['geometry'],
            name=sre_name,
            style_function=lambda feature, color=color_map[sre_name], selected=is_selected: {
                'fillColor': '#ff0000' if selected else color,
                'color': 'black',
                'weight': 3 if selected else 1,
                'fillOpacity': 0.9 if selected else 0.6,
            },
            tooltip=folium.Tooltip(sre_name)
        ).add_to(m)

    return m

# === Interface ===

st.title("Painel das SREs")

# Sidebar ou topo centralizado com filtro
selected_sre = st.selectbox("Selecione a SRE:", options=results_df['sre'].unique())

# Dados da SRE
sre_filtered = results_df[results_df['sre'] == selected_sre]
media_aprov = sre_filtered['perc_aprovados'].mean()
media_reprov = sre_filtered['perc_reprovados'].mean()
media_aband = sre_filtered['perc_abandono'].mean()

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
        


        

# def plot_map_folium(gdf, coluna, titulo, cmap='YlGn'):
#     # Calcular faixa de valores para color scale
#     min_val = gdf[coluna].min()
#     max_val = gdf[coluna].max()

#     # Criar o mapa centralizado no Espírito Santo
#     m = folium.Map(location=[-19.5, -40.7], zoom_start=7, tiles='cartodbpositron')

#     # Criar colormap (pode ajustar cores conforme o cmap desejado)
#     colormap = folium.LinearColormap(
#         colors=['red', 'yellow', 'green'],  # ou usar branca->azul->verde, etc.
#         vmin=min_val,
#         vmax=max_val,
#         caption=titulo
#     )

#     # Adicionar polígonos
#     folium.GeoJson(
#         gdf,
#         style_function=lambda feature: {
#             'fillColor': colormap(feature['properties'][coluna]),
#             'color': 'black',
#             'weight': 0.5,
#             'fillOpacity': 0.7,
#         },
#         tooltip=folium.GeoJsonTooltip(
#             fields=['nm_mun', coluna],
#             aliases=['Município', 'Percentual'],
#             localize=True
#         )
#     ).add_to(m)

#     # Adicionar legenda
#     colormap.add_to(m)

#     # Exibir no Streamlit
#     st_folium(m, width=700, height=500)





   # st.subheader("Visualização no Mapa (Interativo)")
        
        # tab1, tab2, tab3 = st.tabs(['Aprovados', 'Reprovados', 'Abandono'])

        # with tab1:
        #     plot_map_folium(gdf=results_df, coluna="perc_aprovados", titulo="Percentual de Aprovados")

        # with tab2:
        #     plot_map_folium(gdf=results_df, coluna="perc_reprovados", titulo="Percentual de Reprovados")

        # with tab3:
        #     plot_map_folium(gdf=results_df, coluna="perc_abandono", titulo="Percentual de Abandono")



    
        






     

































# st.dataframe(df.head())




