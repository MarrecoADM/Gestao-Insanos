import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Insanos MC - GV", layout="wide")

# COLE O ID DA SUA PLANILHA AQUI:
SHEET_ID = "COLOQUE_AQUI_O_ID_DA_SUA_PLANILHA"
SHEET_NAME = "integrantes"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# Estilo para Celular e PC
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    [data-testid="stMetric"] { background-color: #111; padding: 15px; border-radius: 10px; }
    div.stButton > button { background-color: white; color: black; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (GOOGLE SHEETS) ---
def carregar_dados():
    try:
        return pd.read_csv(URL)
    except:
        return pd.DataFrame(columns=["Nome", "Apelido", "Cargo", "Status", "Comentarios", "Data_Ingresso"])

df_membros = carregar_dados()

# --- SIDEBAR ---
st.sidebar.title("💀 INSANOS GV")
menu = ["Dashboard", "Gestão de Integrantes", "Relatar Evento"]
escolha = st.sidebar.selectbox("Menu", menu)

# --- DASHBOARD ---
if escolha == "Dashboard":
    st.title("Gestão de Divisão")
    c1, c2 = st.columns(2)
    c1.metric("Membros Ativos", len(df_membros[df_membros['Status'] == 'Ativo']))
    c2.metric("Total Cadastrados", len(df_membros))
    
    st.write("### Integrantes por Cargo")
    if not df_membros.empty:
        st.bar_chart(df_membros['Cargo'].value_counts())

# --- GESTÃO ---
elif escolha == "Gestão de Integrantes":
    st.title("Controle de Irmãos")
    
    with st.expander("➕ Novo Cadastro"):
        with st.form("novo", clear_on_submit=True):
            n = st.text_input("Nome")
            a = st.text_input("Apelido")
            c = st.selectbox("Cargo", ["Diretor", "Subdiretor", "Social", "ADM", "GrauX", "FULL VIII", "Stg Armas"])
            s = st.selectbox("Status", ["Ativo", "Afastado"])
            d = st.date_input("Ingresso", format="DD/MM/YYYY")
            
            if st.form_submit_button("Salvar Online"):
                st.info("Para salvar via link, use a integração de escrita do Google Sheets ou edite diretamente na planilha compartilhada.")

    st.write("### Lista de Membros")
    st.dataframe(df_membros, use_container_width=True)
    st.write("🔗 [Clique aqui para editar a Planilha Original](f'https://docs.google.com/spreadsheets/d/{SHEET_ID}')")

# O código para gravar diretamente no Google Sheets exige uma chave de API (Service Account)
# Por segurança em links públicos, a forma mais fácil é ler via CSV e editar via link da planilha.
