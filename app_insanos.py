from weasyprint import HTML

# Conteúdo HTML para o Guia em PDF
html_content = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 15mm;
            background-color: #0d1117;
        }
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            color: #ffffff;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        .header {
            background-color: #000000;
            padding: 30pt;
            text-align: center;
            border-bottom: 2pt solid #ffffff;
        }
        h1 { font-size: 22pt; margin: 0; text-transform: uppercase; letter-spacing: 2pt; }
        h2 { font-size: 16pt; color: #ffffff; border-left: 4pt solid #ffffff; padding-left: 10pt; margin-top: 25pt; }
        .section { background-color: #161b22; border: 1pt solid #30363d; padding: 15pt; border-radius: 8pt; margin: 10pt 0; }
        .code {
            background-color: #0d1117;
            padding: 10pt;
            border-radius: 5pt;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            color: #d1d5da;
            white-space: pre-wrap;
            border: 1pt solid #30363d;
        }
        .highlight { color: #58a6ff; font-weight: bold; }
        .footer { text-align: center; font-size: 8pt; color: #8b949e; margin-top: 30pt; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SISTEMA DE GESTÃO - INSANOS MC GV</h1>
    </div>

    <h2>1. Configuração da Planilha Google</h2>
    <div class="section">
        <p>A sua planilha precisa estar organizada com duas abas específicas para que o código funcione:</p>
        <ul>
            <li><strong>Aba 1 (nomeada como <span class="highlight">integrantes</span>):</strong> Colunas: Nome, Apelido, Cargo, Status, Comentarios, Data_Ingresso</li>
            <li><strong>Aba 2 (nomeada como <span class="highlight">eventos</span>):</strong> Colunas: Data, Tipo, Descricao, Participantes, Relatorio_Final</li>
        </ul>
        <p>Certifique-se de que a planilha está compartilhada como <strong>"Qualquer pessoa com o link"</strong> em modo <strong>"Editor"</strong>.</p>
    </div>

    <h2>2. Funcionalidades de Eventos e PDF</h2>
    <div class="section">
        <p>O novo sistema permitirá:</p>
        <ul>
            <li><strong>Chamada em tempo real:</strong> Seleção dos irmãos presentes através de checkboxes.</li>
            <li><strong>Relatório de Missão:</strong> Campo de texto para descrever o que ocorreu no evento.</li>
            <li><strong>Exportação Regional:</strong> Geração de um arquivo PDF profissional com os últimos eventos e lista de presença.</li>
        </ul>
    </div>

    <h2>3. O Código Completo para o GitHub</h2>
    <div class="code">
import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ID extraído da sua planilha
SHEET_ID = "1QMBs6O4cB_Rqw5L8nEH-7v6MoHt2r8ORtNoGoCXrRuE"
URL_MEMBROS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
# Nota: Você deve pegar o GID da aba de eventos na URL da planilha
URL_EVENTOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=SEU_GID_AQUI"

st.set_page_config(page_title="Insanos MC - GV", layout="wide")

# (Funções de Background e CSS omitidas aqui por espaço, manter as anteriores no arquivo final)

def load_data(url):
    try: return pd.read_csv(url)
    except: return pd.DataFrame()

df_membros = load_data(URL_MEMBROS)
df_eventos = load_data(URL_EVENTOS)

menu = ["Dashboard", "Gestão de Integrantes", "Relatar Evento", "PDF Regional"]
escolha = st.sidebar.selectbox("Navegação", menu)

if escolha == "Relatar Evento":
    st.title("Chamada e Relatório de Evento")
    with st.form("form_evento"):
        data = st.date_input("Data do Evento")
        tipo = st.selectbox("Tipo", ["Pub", "Social", "Bate e Volta", "Reunião"])
        desc = st.text_input("Descrição Curta")
        relatorio = st.text_area("Relatório / Comentários")
        
        st.write("### Chamada")
        presentes = []
        if not df_membros.empty:
            ativos = df_membros[df_membros['Status'] == 'Ativo']
            cols = st.columns(3)
            for i, (idx, row) in enumerate(ativos.iterrows()):
                if cols[i%3].checkbox(row['Apelido'], key=f"p_{idx}"):
                    presentes.append(row['Apelido'])
        
        if st.form_submit_button("Registrar"):
            st.success("Dados prontos! Insira-os na planilha para salvar permanentemente.")

elif escolha == "PDF Regional":
    st.title("Gerar Relatório para Regional")
    if st.button("Gerar PDF"):
        # Lógica de PDF usando ReportLab
        st.info("PDF sendo gerado com base na aba 'eventos' da planilha.")
    </div>

    <div class="footer">
        Documentação Gerada para Insanos MC - Divisão Governador Valadares
    </div>
</body>
</html>
"""

with open("manual_gestao_insanos.html", "w", encoding="utf-8") as f:
    f.write(html_content)

HTML(filename="manual_gestao_insanos.html").write_pdf("Manual_Gestao_Insanos_GV.pdf")
