import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

# --- 1. CONFIGURAÇÃO DA PLANILHA (SEU ID) ---
SHEET_ID = "1QMBs6O4cB_Rqw5L8nEH-7v6MoHt2r8ORtNoGoCXrRuE"
URL_MEMBROS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- 2. FUNÇÕES DE INTERFACE (LOGO E BACKGROUND) ---
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
    /* Deixar os blocos de texto escuros para leitura fácil */
    [data-testid="stForm"], .stDataFrame, [data-testid="stMetric"], .stExpander {{
        background-color: rgba(0, 0, 0, 0.85) !important;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #444;
    }}
    h1, h2, h3, p, span, label {{ color: white !important; text-shadow: 2px 2px 4px #000; }}
    </style>
    ''', unsafe_allow_html=True)

# --- 3. INÍCIO DO APP ---
st.set_page_config(page_title="Insanos MC - GV", layout="wide")

# Aplica o fundo se o arquivo existir no GitHub
if os.path.exists("background.jpg"):
    set_bg('background.jpg')
else:
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)

# --- 4. SIDEBAR COM LOGO PEQUENA ---
if os.path.exists("logo_insanos.png"):
    # width=100 deixa a logo pequena conforme solicitado
    st.sidebar.image("logo_insanos.png", width=120) 
else:
    st.sidebar.title("💀 INSANOS MC")

st.sidebar.subheader("Divisão Gov. Valadares")

# --- 5. CARREGAR DADOS ---
@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL_MEMBROS)
        df['Apelido'] = df['Apelido'].fillna("Sem Nome").astype(str)
        return df
    except:
        return pd.DataFrame()

df_membros = load_data()

# --- 6. MENU DE NAVEGAÇÃO ---
menu = ["Dashboard", "Gestão de Integrantes", "Relatar Evento (Chamada)", "Gerar PDF Regional"]
escolha = st.sidebar.selectbox("Navegação", menu)

# --- DASHBOARD ---
if escolha == "Dashboard":
    st.title("Estatísticas da Divisão")
    if not df_membros.empty:
        c1, c2 = st.columns(2)
        ativos = len(df_membros[df_membros['Status'] == 'Ativo'])
        c1.metric("Integrantes Ativos", ativos)
        c2.metric("Total no Quadro", len(df_membros))
        
        st.write("---")
        st.subheader("Graduações / Cargos")
        st.bar_chart(df_membros['Cargo'].value_counts())
    else:
        st.error("Erro ao carregar dados. Verifique o compartilhamento da planilha.")

# --- GESTÃO ---
elif escolha == "Gestão de Integrantes":
    st.title("Quadro de Membros")
    st.write("🔗 [EDITAR PLANILHA ORIGINAL](https://docs.google.com/spreadsheets/d/" + SHEET_ID + ")")
    st.dataframe(df_membros, use_container_width=True)

# --- CHAMADA ---
elif escolha == "Relatar Evento (Chamada)":
    st.title("Chamada e Missão")
    with st.form("chamada_evento"):
        tipo = st.selectbox("Tipo", ["Pub", "Ação Social", "Bate e Volta", "Reunião"])
        relato = st.text_area("O que aconteceu na missão?")
        
        st.write("### Lista de Presença")
        presencas = []
        if not df_membros.empty:
            membros_ativos = df_membros[df_membros['Status'] == 'Ativo']
            cols = st.columns(4)
            for i, (idx, row) in enumerate(membros_ativos.iterrows()):
                if cols[i % 4].checkbox(row['Apelido'], key=f"p_{idx}"):
                    presencas.append(row['Apelido'])
        
        if st.form_submit_button("Finalizar Chamada"):
            st.success(f"Presenças confirmadas: {', '.join(presencas)}")
            st.info("Copie os dados acima para a aba de eventos da sua planilha.")

# --- PDF ---
elif escolha == "Gerar PDF Regional":
    st.title("Relatório Regional")
    if st.button("📄 Gerar e Baixar PDF"):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        estilos = getSampleStyleSheet()
        elementos = [Paragraph("INSANOS MC - GOVERNADOR VALADARES", estilos['Title']), Spacer(1, 12)]
        
        # Tabela do PDF
        dados_pdf = [["Apelido", "Cargo", "Status"]] + df_membros[["Apelido", "Cargo", "Status"]].values.tolist()
        t = Table(dados_pdf, colWidths=[150, 150, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.black),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elementos.append(t)
        doc.build(elementos)
        
        st.download_button(
            label="Clique aqui para Baixar Arquivo",
            data=buffer.getvalue(),
            file_name=f"Relatorio_GV_{datetime.now().strftime('%d_%m_%Y')}.pdf",
            mime="application/pdf"
        )
