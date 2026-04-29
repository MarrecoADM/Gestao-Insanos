import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Insanos MC - GV", layout="wide")

# 1. COLE O ID DA SUA PLANILHA AQUI:
SHEET_ID = "https://docs.google.com/spreadsheets/d/1QMBs6O4cB_Rqw5L8nEH-7v6MoHt2r8ORtNoGoCXrRuE/edit?gid=0#gid=0"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# --- FUNÇÃO PARA CARREGAR O BACKGROUND ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def set_bg(bin_file):
    bin_str = get_base64(bin_file)
    st.markdown(f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-attachment: fixed;
    }}
    /* Cartões escuros para leitura fácil no celular */
    [data-testid="stForm"], .stDataFrame, [data-testid="stMetric"], .stExpander {{
        background-color: rgba(0, 0, 0, 0.8) !important;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
    }}
    h1, h2, h3, label, p {{ color: white !important; text-shadow: 2px 2px 4px #000; }}
    </style>
    ''', unsafe_allow_html=True)

# Aplica o Fundo se o arquivo existir no GitHub
if os.path.exists("background.jpg"):
    set_bg('background.jpg')

# --- SIDEBAR COM LOGO ---
if os.path.exists("logo_insanos.png"):
    st.sidebar.image("logo_insanos.png")
else:
    st.sidebar.title("💀 INSANOS MC")

# --- CARREGAR DADOS ---
@st.cache_data(ttl=60) # Atualiza os dados a cada 1 minuto
def load_data():
    return pd.read_csv(URL)

try:
    df = load_data()
except:
    st.error("Erro ao conectar com a planilha. Verifique o ID e o compartilhamento.")
    df = pd.DataFrame()

# --- MENU ---
menu = ["Dashboard", "Gestão de Integrantes", "Relatar Evento"]
escolha = st.sidebar.selectbox("Navegação", menu)

if escolha == "Dashboard":
    st.title("Divisão Gov. Valadares")
    if not df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Membros Ativos", len(df[df['Status'] == 'Ativo']))
        c2.metric("Total de Irmãos", len(df))
        
        st.write("### Graduações")
        st.bar_chart(df['Cargo'].value_counts())
    else:
        st.warning("Aguardando dados da planilha...")

elif escolha == "Gestão de Integrantes":
    st.title("Controle de Quadro")
    st.write("🔗 [EDITAR PLANILHA ORIGINAL](https://docs.google.com/spreadsheets/d/" + SHEET_ID + ")")
    st.dataframe(df, use_container_width=True)

elif escolha == "Relatar Evento":
    st.title("Chamada / Relatório")
    st.info("Para registrar eventos via link, edite a aba de eventos na sua Planilha do Google.")
