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

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Insanos MC - GV", layout="wide")

# Link da sua planilha (ajustado para conexão direta)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1QMBs6O4cB_Rqw5L8nEH-7v6MoHt2r8ORtNoGoCXrRuE"

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES DE INTERFACE ---
def set_bg(bin_file):
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

if os.path.exists("background.jpg"):
    set_bg('background.jpg')

if os.path.exists("logo_insanos.png"):
    st.sidebar.image("logo_insanos.png", width=100)

# --- CARREGAR DADOS ---
df_membros = conn.read(spreadsheet=URL_PLANILHA, worksheet="integrantes")
df_eventos = conn.read(spreadsheet=URL_PLANILHA, worksheet="eventos")

menu = ["Dashboard", "Gestão de Integrantes", "Relatar Evento (Chamada)", "Gerar PDF Regional"]
escolha = st.sidebar.selectbox("Navegação", menu)

# --- 1. DASHBOARD ---
if escolha == "Dashboard":
    st.title("Estatísticas da Divisão")
    c1, c2 = st.columns(2)
    c1.metric("Membros Ativos", len(df_membros[df_membros['Status'] == 'Ativo']))
    c2.metric("Eventos Registrados", len(df_eventos))
    st.bar_chart(df_membros['Cargo'].value_counts())

# --- 2. GESTÃO DE INTEGRANTES ---
elif escolha == "Gestão de Integrantes":
    st.title("Cadastro de Irmãos")
    
    with st.expander("➕ Adicionar Novo Integrante"):
        with st.form("add_membro"):
            nome = st.text_input("Nome Completo")
            apelido = st.text_input("Apelido")
            cargo = st.selectbox("Cargo", ["Diretor", "Subdiretor", "Social", "ADM", "GrauX", "FULL VIII"])
            status = st.selectbox("Status", ["Ativo", "Afastado"])
            coment = st.text_area("Comentários")
            
            if st.form_submit_button("Salvar na Planilha"):
                nova_linha = pd.DataFrame([{"Nome": nome, "Apelido": apelido, "Cargo": cargo, "Status": status, "Comentarios": coment, "Data_Ingresso": datetime.now().strftime("%d/%m/%Y")}])
                updated_df = pd.concat([df_membros, nova_linha], ignore_index=True)
                conn.update(spreadsheet=URL_PLANILHA, worksheet="integrantes", data=updated_df)
                st.success("Integrante salvo com sucesso!")
                st.rerun()

    st.write("### Quadro Atual")
    st.dataframe(df_membros, use_container_width=True)

# --- 3. RELATAR EVENTO ---
elif escolha == "Relatar Evento (Chamada)":
    st.title("Chamada e Relatório")
    with st.form("form_evento"):
        tipo = st.selectbox("Tipo", ["Pub", "Ação Social", "Bate e Volta", "Reunião"])
        relato = st.text_area("Relatório da Missão")
        
        st.write("### Presença")
        presencas = []
        ativos = df_membros[df_membros['Status'] == 'Ativo']
        cols = st.columns(4)
        for i, (idx, row) in enumerate(ativos.iterrows()):
            if cols[i % 4].checkbox(row['Apelido'], key=f"p_{idx}"):
                presencas.append(row['Apelido'])
        
        if st.form_submit_button("Gravar Evento na Planilha"):
            novo_evento = pd.DataFrame([{
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Tipo": tipo,
                "Descricao": relato,
                "Participantes": ", ".join(presencas)
            }])
            updated_eventos = pd.concat([df_eventos, novo_evento], ignore_index=True)
            conn.update(spreadsheet=URL_PLANILHA, worksheet="eventos", data=updated_eventos)
            st.success("Evento e Presenças gravados com sucesso!")
            st.rerun()

# --- 4. GERAR PDF ---
elif escolha == "Gerar PDF Regional":
    st.title("Relatório Regional")
    if st.button("📄 Baixar PDF"):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elementos = [Paragraph("INSANOS MC - GV", getSampleStyleSheet()['Title']), Spacer(1, 12)]
        
        dados_pdf = [["Data", "Evento", "Participantes"]]
        for _, row in df_eventos.tail(10).iterrows():
            dados_pdf.append([row['Data'], row['Tipo'], row['Participantes'][:40] + "..."])
        
        t = Table(dados_pdf, colWidths=[80, 80, 240])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.black), ('TEXTCOLOR',(0,0),(-1,0), colors.whitesmoke), ('GRID',(0,0),(-1,-1),1,colors.black)]))
        elementos.append(t)
        doc.build(elementos)
        st.download_button("Clique aqui para Baixar PDF", buffer.getvalue(), "Relatorio_Regional.pdf", "application/pdf")
