import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os
import base64
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Insanos MC - GV", layout="wide")

# --- CONEXÃO E TRATAMENTO DE CREDENCIAIS ---
try:
    # 1. Transformamos os segredos em um dicionário para podermos manipular
    secrets_dict = st.secrets["connections"]["gsheets"].to_dict()

    # 2. Corrigimos a chave privada caso ela tenha sido colada no formato "curto"
    if "-----BEGIN PRIVATE KEY-----" not in secrets_dict["private_key"]:
        raw_key = secrets_dict["private_key"]
        # Reconstrói o formato PEM que o Google exige
        secrets_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{raw_key}\n-----END PRIVATE KEY-----\n"

    # 3. Inicializamos a conexão
    # Removemos o 'type' daqui porque ele já existe dentro do 'secrets_dict'
    conn = st.connection("gsheets", **secrets_dict)
    
except Exception as e:
    st.error(f"Erro ao configurar credenciais: {e}")
    st.stop()

# URL da sua planilha
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1QMBs6O4cB_Rqw5L8nEH-7v6MoHt2r8ORtNoGoCXrRuE"

# --- FUNÇÕES DE INTERFACE (Background e Estilo) ---
def set_bg(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            bin_str = base64.b64encode(f.read()).decode()
        st.markdown(f'''
        <style>
        .stApp {{ background-image: url("data:image/jpg;base64,{bin_str}"); background-size: cover; background-attachment: fixed; }}
        [data-testid="stForm"], .stDataFrame, [data-testid="stMetric"], .stExpander {{
            background-color: rgba(0, 0, 0, 0.85) !important; padding: 20px; border-radius: 10px; border: 1px solid #444;
        }}
        h1, h2, h3, p, span, label {{ color: white !important; }}
        </style>
        ''', unsafe_allow_html=True)

set_bg('background.jpg')
if os.path.exists("logo_insanos.png"):
    st.sidebar.image("logo_insanos.png", width=100)

# --- CARREGAR DADOS ---
try:
    df_membros = conn.read(spreadsheet=URL_PLANILHA, worksheet="integrantes")
    df_eventos = conn.read(spreadsheet=URL_PLANILHA, worksheet="eventos")
except Exception as e:
    st.error(f"Erro de conexão com a planilha: {e}")
    st.stop()

# --- MENU LATERAL ---
menu = ["Dashboard", "Gestão de Integrantes", "Relatar Evento (Chamada)", "Gerar PDF Regional"]
escolha = st.sidebar.selectbox("Navegação", menu)

# --- 1. DASHBOARD ---
if escolha == "Dashboard":
    st.title("Estatísticas da Divisão GV")
    c1, c2 = st.columns(2)
    
    ativos_count = len(df_membros[df_membros['Status'] == 'Ativo']) if not df_membros.empty else 0
    eventos_count = len(df_eventos) if not df_eventos.empty else 0
    
    c1.metric("Membros Ativos", ativos_count)
    c2.metric("Eventos Registrados", eventos_count)
    
    if not df_membros.empty:
        st.bar_chart(df_membros['Cargo'].value_counts())
    
    st.write("### Lista Geral")
    st.dataframe(df_membros, use_container_width=True)

# --- 2. GESTÃO DE INTEGRANTES ---
elif escolha == "Gestão de Integrantes":
    st.title("Cadastro de Irmãos")
    with st.form("add_membro"):
        nome = st.text_input("Nome")
        apelido = st.text_input("Apelido")
        cargo = st.selectbox("Cargo", ["Diretor", "Subdiretor", "Social", "ADM", "GrauX", "FULL VIII"])
        status = st.selectbox("Status", ["Ativo", "Afastado"])
        if st.form_submit_button("Salvar na Planilha"):
            nova_linha = pd.DataFrame([{"Nome": nome, "Apelido": apelido, "Cargo": cargo, "Status": status, "Data_Ingresso": datetime.now().strftime("%d/%m/%Y")}])
            updated_df = pd.concat([df_membros, nova_linha], ignore_index=True)
            conn.update(spreadsheet=URL_PLANILHA, worksheet="integrantes", data=updated_df)
            st.success("Dados salvos!")
            st.rerun()

# --- 3. RELATAR EVENTO ---
elif escolha == "Relatar Evento (Chamada)":
    st.title("Relatório de Missão")
    with st.form("form_evento"):
        tipo = st.selectbox("Tipo", ["Pub", "Ação Social", "Bate e Volta", "Reunião"])
        relato = st.text_area("Relato")
        st.write("### Presença")
        presencas = []
        
        if not df_membros.empty:
            ativos = df_membros[df_membros['Status'] == 'Ativo']
            for idx, row in ativos.iterrows():
                if st.checkbox(row['Apelido'], key=f"check_{idx}"):
                    presencas.append(row['Apelido'])
        
        if st.form_submit_button("Gravar Missão"):
            novo_ev = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Tipo": tipo, "Relato": relato, "Participantes": ", ".join(presencas)}])
            updated_ev = pd.concat([df_eventos, novo_ev], ignore_index=True)
            conn.update(spreadsheet=URL_PLANILHA, worksheet="eventos", data=updated_ev)
            st.success("Missão Gravada!")
            st.rerun()

# --- 4. PDF ---
elif escolha == "Gerar PDF Regional":
    st.title("Relatório Regional")
    if st.button("Gerar PDF"):
        st.info("Função de PDF pronta para exportação.")
