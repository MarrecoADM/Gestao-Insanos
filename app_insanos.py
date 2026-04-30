import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os
import base64
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Insanos MC - GV", layout="wide")

# Link da sua planilha
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1QMBs6O4cB_Rqw5L8nEH-7v6MoHt2r8ORtNoGoCXrRuE"

# Conexão oficial via Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INTERFACE ---
def set_bg(bin_file):
    with open(bin_file, 'rb') as f:
        bin_str = base64.b64encode(f.read()).decode()
    st.markdown(f'''<style>.stApp {{ background-image: url("data:image/jpg;base64,{bin_str}"); background-size: cover; background-attachment: fixed; }}
    [data-testid="stForm"], .stDataFrame, [data-testid="stMetric"], .stExpander {{ background-color: rgba(0, 0, 0, 0.85) !important; padding: 20px; border-radius: 10px; border: 1px solid #444; }}
    h1, h2, h3, p, span, label {{ color: white !important; }}</style>''', unsafe_allow_html=True)

if os.path.exists("background.jpg"): set_bg('background.jpg')
if os.path.exists("logo_insanos.png"): st.sidebar.image("logo_insanos.png", width=100)

# --- CARREGAR DADOS COM TRATAMENTO DE ERRO ---
try:
    df_membros = conn.read(spreadsheet=URL_PLANILHA, worksheet="integrantes")
    df_eventos = conn.read(spreadsheet=URL_PLANILHA, worksheet="eventos")
except Exception as e:
    st.error("Erro de Autenticação. Verifique se o e-mail da 'Conta de Serviço' foi adicionado como Editor na planilha.")
    st.stop()

menu = ["Dashboard", "Gestão de Integrantes", "Relatar Evento", "PDF Regional"]
escolha = st.sidebar.selectbox("Menu", menu)

if escolha == "Dashboard":
    st.title("Gestão Divisão GV")
    c1, c2 = st.columns(2)
    c1.metric("Membros Ativos", len(df_membros[df_membros['Status'] == 'Ativo']))
    c2.metric("Eventos", len(df_eventos))
    st.bar_chart(df_membros['Cargo'].value_counts())

elif escolha == "Gestão de Integrantes":
    st.title("Cadastro")
    with st.form("add"):
        apelido = st.text_input("Apelido")
        cargo = st.selectbox("Cargo", ["Diretor", "Subdiretor", "Social", "ADM", "GrauX", "FULL VIII"])
        status = st.selectbox("Status", ["Ativo", "Afastado"])
        if st.form_submit_button("Salvar na Planilha"):
            nova_linha = pd.DataFrame([{"Apelido": apelido, "Cargo": cargo, "Status": status, "Data_Ingresso": datetime.now().strftime("%d/%m/%Y")}])
            updated = pd.concat([df_membros, nova_linha], ignore_index=True)
            conn.update(spreadsheet=URL_PLANILHA, worksheet="integrantes", data=updated)
            st.success("Salvo!")
            st.rerun()
    st.dataframe(df_membros)

elif escolha == "Relatar Evento":
    st.title("Chamada")
    with st.form("evento"):
        relato = st.text_area("Relatório")
        participantes = []
        ativos = df_membros[df_membros['Status'] == 'Ativo']
        cols = st.columns(4)
        for i, (idx, row) in enumerate(ativos.iterrows()):
            if cols[i % 4].checkbox(row['Apelido'], key=f"p_{idx}"):
                participantes.append(row['Apelido'])
        
        if st.form_submit_button("Gravar Missão"):
            novo_ev = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": relato, "Participantes": ", ".join(participantes)}])
            updated_ev = pd.concat([df_eventos, novo_ev], ignore_index=True)
            conn.update(spreadsheet=URL_PLANILHA, worksheet="eventos", data=updated_ev)
            st.success("Evento Gravado!")
