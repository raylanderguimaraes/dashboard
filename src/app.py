import streamlit as st
import pandas as pd


# Iniciar projeto
# Escolher base de dados
# Pesquisar como faz para utilizar o streamlit e hospedar 



csv_path = r"C:\Users\rgramos\pos_mineracao\dashboard\src\data\microdados_ed_basica_2024.csv"
df = pd.read_csv(csv_path, sep=";", encoding="latin1")

st.write(df.head())


year = [2013, 2014]

with st.sidebar:
     st.write("Painel")
     st.selectbox("Escolha o Ano", year)




