import streamlit as st
import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from scraper import run_watcher

# 1. Configurações de Ambiente
load_dotenv()
url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not url or not key:
    st.error("Erro: Credenciais do Supabase não encontradas.")
    st.stop()

supabase: Client = create_client(url, key)
st.set_page_config(page_title="Cert-Manager Pro", page_icon="🚀", layout="wide")

# 2. Funções de Backend
def get_dashboard_data():
    certs = supabase.table("certifications").select("*").order("id").execute()
    wallet = supabase.table("study_wallet").select("balance_brl").order("id", desc=True).limit(1).execute()
    history = supabase.table("alert_history").select("*").order("alert_date", desc=True).limit(5).execute()
    balance = float(wallet.data[0]['balance_brl']) if wallet.data else 0.0
    return certs.data, balance, history.data

def get_dollar_rate():
    try:
        res = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()
        return float(res['USDBRL']['bid'])
    except:
        return 5.15

# 3. Processamento
dolar = get_dollar_rate()
certs, current_balance, alerts_history = get_dashboard_data()

# 4. Interface do Usuário
st.title("🚀 Cert-Manager: Roadmap Pleno")

m1, m2, m3 = st.columns(3)
m1.metric("Cotação USD/BRL", f"R$ {dolar:.2f}")
m2.metric("Saldo em Carteira", f"R$ {current_balance:.2f}")
m3.metric("Foco Carreira", "Identity & Security (SC-300)")

st.sidebar.header("⚙️ Painel de Controle")
with st.sidebar.form("deposit_form"):
    deposit = st.number_input("Novo aporte (R$):", min_value=0.0, step=50.0)
    if st.form_submit_button("Confirmar Depósito"):
        new_total = current_balance + deposit
        supabase.table("study_wallet").insert({"balance_brl": new_total}).execute()
        st.success("Saldo atualizado!")
        st.rerun()

if st.sidebar.button("🔍 Executar Varredura Global"):
    with st.sidebar.status("Varrendo múltiplas fontes..."):
        result = run_watcher()
        st.sidebar.success("Busca finalizada!")
        st.rerun()

# 5. Roadmap com Wiki e Labs Integrados
st.subheader("🎯 Minha Trilha Microsoft")

for cert in certs:
    price_brl = float(cert['price_usd']) * dolar
    progress = min(current_balance / price_brl, 1.0) if price_brl > 0 else 0
    
    with st.expander(f"📌 {cert['name']} - {cert['status']}"):
        col_info, col_lab = st.columns([1, 1.5])
        
        with col_info:
            st.markdown("#### 💰 Financeiro")
            st.write(f"**Investimento:** R$ {price_brl:.2f}")
            st.progress(progress)
            
            st.markdown("#### 🔗 Links Oficiais")
            if cert.get('exam_url'):
                st.link_button("Microsoft Learn", cert['exam_url'])
            
            # Link dinâmico para os Labs oficiais no GitHub da Microsoft
            lab_repo = cert['name'].split(' ')[0].replace('-', '')
            st.link_button("📂 Labs Oficiais (GitHub)", f"https://github.com/MicrosoftLearning/{lab_repo}")

        with col_lab:
            st.markdown("#### 🧪 Guia de Laboratório (Wiki)")
            # Exibe o conteúdo da coluna 'lab_guide' que criamos no Supabase
            if cert.get('lab_guide'):
                st.markdown(cert['lab_guide'])
            else:
                st.info("Aguardando definição de roteiro prático.")
            
            if "SC-300" in cert['name']:
                st.caption("Foco: Reestruturação de Identidades Híbridas (AD Connect)")

        st.write("---")
        st.caption(f"Categoria: {cert['category']} | Monitoramento ativo via Web Watcher")

# 6. Histórico de Oportunidades
st.write("---")
st.subheader("📜 Últimas Oportunidades Detectadas")
if alerts_history:
    for alert in alerts_history:
        st.markdown(f"**{alert['alert_date'][:10]} - {alert['source_name']}**")
        st.write(f"Achados: `{alert['found_keywords']}`")
        st.link_button(f"Verificar Fonte", alert['url'])
        st.write("")