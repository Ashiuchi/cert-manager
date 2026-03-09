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
    
    # Busca links dinâmicos
    links = supabase.table("cert_links").select("*").execute()
    
    balance = float(wallet.data[0]['balance_brl']) if wallet.data else 0.0
    return certs.data, balance, history.data, links.data

def get_dollar_rate():
    try:
        res = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()
        return float(res['USDBRL']['bid'])
    except:
        return 5.15

# 3. Processamento
dolar = get_dollar_rate()
certs, current_balance, alerts_history, all_links = get_dashboard_data()

# 4. Interface (Métricas)
st.title("🚀 Cert-Manager: Roadmap Pleno")
m1, m2, m3 = st.columns(3)
m1.metric("Cotação USD/BRL", f"R$ {dolar:.2f}")
m2.metric("Saldo em Carteira", f"R$ {current_balance:.2f}")
m3.metric("Foco Carreira", "Identity & Security (SC-300)")

# Sidebar
st.sidebar.header("⚙️ Painel de Controle")
if st.sidebar.button("🔍 Executar Varredura Global"):
    with st.sidebar.status("Varrendo múltiplas fontes..."):
        run_watcher()
        st.sidebar.success("Busca finalizada!")
        st.rerun()

# 5. Roadmap com Links Dinâmicos e Labs
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
            
            st.markdown("#### 🔗 Recursos e Links")
            # Lista links salvos no banco para esta cert
            cert_specific_links = [l for l in all_links if l['cert_id'] == cert['id']]
            for l in cert_specific_links:
                st.link_button(f"🔗 {l['link_name']}", l['url'])
            
            # Formulário para adicionar novo link
            with st.popover("➕ Adicionar Recurso"):
                new_name = st.text_input("Nome (ex: GitHub Labs)", key=f"name_{cert['id']}")
                new_url = st.text_input("URL", key=f"url_{cert['id']}")
                if st.button("Salvar Link", key=f"btn_{cert['id']}"):
                    if new_name and new_url:
                        supabase.table("cert_links").insert({
                            "cert_id": cert['id'], 
                            "link_name": new_name, 
                            "url": new_url
                        }).execute()
                        st.success("Link adicionado!")
                        st.rerun()

        with col_lab:
            st.markdown(f"#### 🧪 Lab & Study Guide")
            if cert.get('lab_guide'):
                lines = cert['lab_guide'].split('\n')
                tasks = [line.replace('- [ ]', '').strip() for line in lines if line.startswith('- [ ]')]
                
                if tasks:
                    completed_tasks = 0
                    for i, task in enumerate(tasks):
                        if st.checkbox(task, key=f"task_{cert['id']}_{i}"):
                            completed_tasks += 1
                    
                    progress_pct = completed_tasks / len(tasks) if tasks else 0
                    st.write(f"**Progresso do Lab:** {progress_pct*100:.0f}%")
                    st.progress(progress_pct)
                
                other_content = "\n".join([line for line in lines if not line.startswith('- [ ]')])
                if other_content.strip():
                    st.markdown(other_content)

# 6. Histórico
st.write("---")
st.subheader("📜 Últimas Oportunidades")
if alerts_history:
    for alert in alerts_history:
        st.markdown(f"**{alert['alert_date'][:10]} - {alert['source_name']}**")
        st.write(f"Achados: `{alert['found_keywords']}`")
        st.link_button(f"Verificar Fonte", alert['url'])