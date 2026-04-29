import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

# --- CONFIGURAÇÃO DA PLANILHA ---
# Link da sua planilha que você enviou
SHEET_ID = "1QMBs6O4cB_Rqw5L8nEH-7v6MoHt2r8ORtNoGoCXrRuE"

# GID é o número que aparece no final do link da planilha para cada aba
# GID 0 costuma ser a primeira aba (integrantes)
URL_MEMBROS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

st.set_page_config(page_title="Insanos MC - GV", layout="wide")

# Estilo Visual (Preto e Branco Insanos)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    [data-testid="stMetric"] { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    div.stButton > button { background-color: white; color: black; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
@st.cache_data(ttl=60)
def carregar_membros():
    try:
        df = pd.read_csv(URL_MEMBROS)
        df['Apelido'] = df['Apelido'].fillna("Sem Apelido").astype(str)
        return df
    except:
        return pd.DataFrame(columns=["Nome", "Apelido", "Cargo", "Status"])

df_membros = carregar_membros()

# --- MENU LATERAL ---
st.sidebar.title("💀 INSANOS MC - GV")
menu = ["Dashboard", "Gestão de Integrantes", "Relatar Evento (Chamada)", "Gerar PDF Regional"]
escolha = st.sidebar.selectbox("Navegação", menu)

# --- 1. DASHBOARD ---
if escolha == "Dashboard":
    st.title("Painel de Controle Divisão GV")
    c1, c2 = st.columns(2)
    
    if not df_membros.empty:
        ativos = len(df_membros[df_membros['Status'] == 'Ativo'])
        c1.metric("Integrantes Ativos", ativos)
        c2.metric("Total no Quadro", len(df_membros))
        
        st.write("### Distribuição de Cargos")
        st.bar_chart(df_membros['Cargo'].value_counts())

# --- 2. GESTÃO DE INTEGRANTES ---
elif escolha == "Gestão de Integrantes":
    st.title("Quadro de Integrantes")
    st.info("Para alterar dados, use o link da planilha abaixo:")
    st.link_button("Ir para Planilha Google", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}")
    st.dataframe(df_membros, use_container_width=True)

# --- 3. RELATAR EVENTO ---
elif escolha == "Relatar Evento (Chamada)":
    st.title("Chamada de Evento")
    with st.form("evento_form"):
        tipo = st.selectbox("Tipo de Evento", ["Pub", "Ação Social", "Reunião", "Bate e Volta"])
        data_ev = st.date_input("Data")
        relato = st.text_area("Relatório da Missão")
        
        st.write("### Presença")
        participantes = []
        if not df_membros.empty:
            ativos_lista = df_membros[df_membros['Status'] == 'Ativo']
            cols = st.columns(3)
            for i, (idx, row) in enumerate(ativos_lista.iterrows()):
                if cols[i % 3].checkbox(row['Apelido'], key=f"check_{idx}"):
                    participantes.append(row['Apelido'])
        
        if st.form_submit_button("Confirmar Chamada"):
            st.success(f"Evento registrado! Copie os nomes para a planilha: {', '.join(participantes)}")

# --- 4. GERAR PDF ---
elif escolha == "Gerar PDF Regional":
    st.title("Relatório para Regional")
    st.write("Gera um PDF baseado nos dados atuais dos integrantes.")
    
    if st.button("📄 Baixar PDF"):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        elements.append(Paragraph("RELATÓRIO OFICIAL - INSANOS MC GV", styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Tabela de Integrantes
        data = [["Apelido", "Cargo", "Status"]] + df_membros[["Apelido", "Cargo", "Status"]].values.tolist()
        t = Table(data, colWidths=[150, 150, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))
        elements.append(t)
        
        doc.build(elements)
        st.download_button(
            label="Clique para Salvar o PDF",
            data=buffer.getvalue(),
            file_name=f"Relatorio_Insanos_GV_{datetime.now().strftime('%d_%m_%Y')}.pdf",
            mime="application/pdf"
        )
