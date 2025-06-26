import streamlit as st
import pandas as pd


paths = [
    {
        "id": 1,
        "path_name": r"C:\Users\rgramos\pos_mineracao\dashboard\src\data\df_es_filtrado_2021.1.csv"
    },
    {
         "id": 2,
         "path_name": r"C:\Users\rgramos\pos_mineracao\dashboard\src\data\df_es_filtrado_2023.1.csv"
    }
]

years = [2021, 2023]

@st.cache_data
def open_csv(year):
     if (year == 2021):
          df = pd.read_csv(paths[0]['path_name'], sep=";", encoding='latin1')
     elif (year == 2023):
          df = pd.read_csv(paths[1]['path_name'], sep=';', encoding='latin1')
     else:
        raise ValueError("Ano não suportado.")
     return df


with st.sidebar:
     st.write("Painel")
     selected_year = st.selectbox("Escolha o Ano", years)



features = ["ID_REGIAO",
"ID_UF",
"IN_PUBLICA",
"ID_AREA",
"PROFICIENCIA_LP_SAEB",
"PROFICIENCIA_MT_SAEB"]

#Renomear as colunas com nomes que sejam mais amigáveis
df = open_csv(selected_year)


st.markdown("**Estatísticas básicas**")
st.dataframe(df.head())

col1, col2 = st.columns(2)

with col1:

     

































# st.dataframe(df.head())




