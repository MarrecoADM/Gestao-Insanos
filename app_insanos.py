import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# --- FUNÇÕES DE INTERFACE (BACKGROUND E LOGO) ---
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
    [data-testid="stForm"], .stDataFrame, .stMetric, .stExpander {{
        background-color: rgba(0, 0, 0, 0.85) !important;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #444;
    }}
    h1, h2, h3, p, span, label {{ color: white !important; }}
    </style>
    ''', unsafe_allow_html=True)

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Insanos MC - GV", layout="wide")

if os.path.exists("background.jpg"):
    try: set_bg('background.jpg')
    except: st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
MEMBROS_DB = "integrantes_gv.csv"
EVENTOS_DB = "historico_eventos.csv"
LISTA_CARGOS = ["Diretor", "Subdiretor", "Social", "ADM", "GrauX", "GrauX PP", "GrauX meio", "FULL VIII", "Stg Armas"]

def carregar_dados():
    # Carregar Membros
    if not os.path.exists(MEMBROS_DB):
        df = pd.DataFrame(columns=["Nome", "Apelido", "Cargo", "Status", "Comentarios", "Data_Ingresso"])
        df.to_csv(MEMBROS_DB, index=False)
    
    df_m = pd.read_csv(MEMBROS_DB)
    # Garantir que a coluna de data de ingresso exista
    if "Data_Ingresso" not in df_m.columns:
        df_m["Data_Ingresso"] = datetime.now().strftime("%d/%m/%Y")
        df_m.to_csv(MEMBROS_DB, index=False)
    
    # Limpeza de nomes nulos
    df_m['Apelido'] = df_m['Apelido'].fillna("Sem Nome").astype(str)
    
    # Carregar Eventos
    if not os.path.exists(EVENTOS_DB):
        pd.DataFrame(columns=["Data", "Tipo", "Descricao", "Participantes"]).to_csv(EVENTOS_DB, index=False)
    df_e = pd.read_csv(EVENTOS_DB)
    
    return df_m, df_e

df_membros, df_eventos = carregar_dados()

# --- SIDEBAR ---
if os.path.exists("logo_insanos.png"):
    st.sidebar.image("logo_insanos.png")
else:
    st.sidebar.title("💀 INSANOS MC")

menu = ["Dashboard", "Gestão de Integrantes", "Relatar Evento (Chamada)", "Gerar PDF Regional"]
escolha = st.sidebar.selectbox("Navegação", menu)

# --- 1. DASHBOARD ---
if escolha == "Dashboard":
    st.title("Estatísticas da Divisão GV")
    
    # Cálculos para o mês atual
    hoje = datetime.now()
    mes_atual = hoje.strftime("%m/%Y")
    # Converter para string para comparar com o CSV
    novos_mes = df_membros[df_membros['Data_Ingresso'].str.contains(f"/{hoje.month:02d}/", na=False)]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Membros Ativos", len(df_membros[df_membros['Status'] == 'Ativo']))
    c2.metric("Eventos Registrados", len(df_eventos))
    c3.metric("Entradas no Mês", len(novos_mes))
    
    st.write("---")
    st.subheader("Distribuição por Cargos/Graduações")
    if not df_membros.empty:
        contagem = df_membros['Cargo'].value_counts()
        st.bar_chart(contagem)

    st.write("### Últimos Integrantes Cadastrados")
    st.table(df_membros[["Apelido", "Cargo", "Data_Ingresso"]].tail(5))

# --- 2. GESTÃO DE INTEGRANTES ---
elif escolha == "Gestão de Integrantes":
    st.title("Controle de Quadro e Datas")
    
    with st.expander("➕ Cadastrar Novo Irmão"):
        with st.form("add_membro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo")
            apelido = col2.text_input("Apelido / Nome de Estrada")
            cargo = col1.selectbox("Cargo/Graduação", LISTA_CARGOS)
            status = col2.selectbox("Status", ["Ativo", "Afastado", "Desligado"])
            data_ing = st.date_input("Data de Ingresso na Divisão", format="DD/MM/YYYY")
            coment = st.text_area("Comentários")
            
            if st.form_submit_button("Salvar no Drive"):
                if apelido:
                    nova_data = data_ing.strftime("%d/%m/%Y")
                    novo = pd.DataFrame([{"Nome": nome, "Apelido": apelido, "Cargo": cargo, "Status": status, "Comentarios": coment, "Data_Ingresso": nova_data}])
                    df_membros = pd.concat([df_membros, novo], ignore_index=True)
                    df_membros.to_csv(MEMBROS_DB, index=False)
                    st.success(f"{apelido} salvo com sucesso!")
                    st.rerun()

    st.write("### Edição de Dados (DD/MM/AAAA)")
    edit_df = st.data_editor(df_membros, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sincronizar Alterações"):
        edit_df.to_csv(MEMBROS_DB, index=False)
        st.success("Arquivos atualizados no Google Drive!")

# --- 3. RELATAR EVENTO ---
elif escolha == "Relatar Evento (Chamada)":
    st.title("Chamada e Relatório")
    with st.form("evento"):
        tipo = st.selectbox("Tipo", ["Pub", "Ação Social", "Bate e Volta", "Viagem", "Reunião"])
        data_ev = st.date_input("Data do Evento", format="DD/MM/YYYY")
        resumo = st.text_area("Relatório da Missão")
        
        st.write("### Chamada")
        ativos = df_membros[df_membros['Status'] == 'Ativo']
        checks = []
        cols = st.columns(4)
        for i, (idx, row) in enumerate(ativos.iterrows()):
            label = str(row['Apelido'])
            if cols[i % 4].checkbox(label, key=f"p_{idx}"):
                checks.append(label)
        
        if st.form_submit_button("Gravar Evento"):
            data_str = data_ev.strftime("%d/%m/%Y")
            novo_ev = pd.DataFrame([{"Data": data_str, "Tipo": tipo, "Descricao": resumo, "Participantes": ", ".join(checks)}])
            df_eventos = pd.concat([df_eventos, novo_ev], ignore_index=True)
            df_eventos.to_csv(EVENTOS_DB, index=False)
            st.success("Evento registrado!")

# --- 4. GERAR PDF ---
elif escolha == "Gerar PDF Regional":
    st.title("Exportação Regional")
    if st.button("📄 Gerar PDF Oficial"):
        nome_pdf = f"Relatorio_GV_{datetime.now().strftime('%d_%m_%Y')}.pdf"
        doc = SimpleDocTemplate(nome_pdf, pagesize=A4)
        estilos = getSampleStyleSheet()
        elementos = [Paragraph("INSANOS MC - GOVERNADOR VALADARES", estilos['Title']), Spacer(1, 12)]
        
        # Tabela Membros
        dados = [["Apelido", "Cargo", "Ingresso"]] + df_membros[["Apelido", "Cargo", "Data_Ingresso"]].fillna("").values.tolist()
        t = Table(dados, colWidths=[150, 150, 100])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.black), ('TEXTCOLOR',(0,0),(-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
        elementos.append(t)
        
        doc.build(elements)
        st.success(f"PDF Gerado: {nome_pdf}")