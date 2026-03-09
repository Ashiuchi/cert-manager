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

# --- SISTEMA DE USUÁRIO ---
st.sidebar.header("👤 Identificação")
user = st.sidebar.text_input("Seu Nome:", value="Alessandro")
st.sidebar.caption(f"Logado como: {user}")

# 2. Funções de Backend (Filtradas por Usuário)
def get_dashboard_data(user_name):
    certs = supabase.table("certifications").select("*").order("id").execute()
    wallet = supabase.table("study_wallet").select("balance_brl").eq("user_name", user_name).order("id", desc=True).limit(1).execute()
    history = supabase.table("alert_history").select("*").order("alert_date", desc=True).limit(5).execute()
    links = supabase.table("cert_links").select("*").eq("user_name", user_name).execute()
    
    # Busca o progresso dos checkboxes do usuário
    progress = supabase.table("user_progress").select("*").eq("user_name", user_name).execute()
    
    balance = float(wallet.data[0]['balance_brl']) if wallet.data else 0.0
    return certs.data, balance, history.data, links.data, progress.data

def get_dollar_rate():
    try:
        res = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()
        return float(res['USDBRL']['bid'])
    except: return 5.15

# 3. Processamento
dolar = get_dollar_rate()
certs, current_balance, alerts_history, all_links, user_progress = get_dashboard_data(user)

# 4. Interface (Métricas)
st.title(f"🚀 Cert-Manager: Roadmap de {user}")
m1, m2, m3 = st.columns(3)
m1.metric("Cotação USD/BRL", f"R$ {dolar:.2f}")
m2.metric("Seu Saldo", f"R$ {current_balance:.2f}")
m3.metric("Status", "🔥 Em Estudos")

# Sidebar - Ações
st.sidebar.header("⚙️ Painel de Controle")
with st.sidebar.form("deposit_form"):
    deposit = st.number_input("Novo aporte (R$):", min_value=0.0, step=50.0)
    if st.form_submit_button("Confirmar Depósito"):
        supabase.table("study_wallet").insert({"balance_brl": current_balance + deposit, "user_name": user}).execute()
        st.rerun()

# 5. Roadmap
st.subheader("🎯 Trilhas de Estudo Personalizadas")

for cert in certs:
    price_brl = float(cert['price_usd']) * dolar
    progress_fin = min(current_balance / price_brl, 1.0) if price_brl > 0 else 0
    
    with st.expander(f"📌 {cert['name']} - {cert['status']}"):
        col_info, col_lab = st.columns([1, 1.5])
        
        with col_info:
            st.markdown("#### 💰 Financeiro Individual")
            st.write(f"**Investimento:** R$ {price_brl:.2f}")
            st.progress(progress_fin)
            
            st.markdown("#### 🔗 Meus Recursos")
            cert_specific_links = [l for l in all_links if l['cert_id'] == cert['id']]
            for l in cert_specific_links:
                st.link_button(f"📄 {l['link_name']}", l['url'])
            
            with st.popover("➕ Adicionar Recurso"):
                new_name = st.text_input("Nome", key=f"n_{cert['id']}")
                new_url = st.text_input("URL", key=f"u_{cert['id']}")
                if st.button("Salvar", key=f"b_{cert['id']}"):
                    supabase.table("cert_links").insert({"cert_id": cert['id'], "link_name": new_name, "url": new_url, "user_name": user}).execute()
                    st.rerun()

        with col_lab:
            st.markdown(f"#### 🧪 Meu Progresso Prático")
            if cert.get('lab_guide'):
                lines = cert['lab_guide'].split('\n')
                tasks = [line.replace('- [ ]', '').strip() for line in lines if line.startswith('- [ ]')]
                
                if tasks:
                    completed_count = 0
                    for i, task in enumerate(tasks):
                        # Verifica se esta tarefa já está marcada no banco para este usuário
                        is_done = any(p['cert_id'] == cert['id'] and p['task_index'] == i and p['is_completed'] for p in user_progress)
                        
                        if st.checkbox(task, value=is_done, key=f"chk_{user}_{cert['id']}_{i}"):
                            completed_count += 1
                            if not is_done: # Se marcou agora, salva no banco
                                supabase.table("user_progress").upsert({"user_name": user, "cert_id": cert['id'], "task_index": i, "is_completed": True}).execute()
                        elif is_done: # Se desmarcou, remove do banco
                            supabase.table("user_progress").upsert({"user_name": user, "cert_id": cert['id'], "task_index": i, "is_completed": False}).execute()
                    
                    st.progress(completed_count / len(tasks) if tasks else 0)

# 6. Histórico Global (Oportunidades aparecem para todos)
st.write("---")
st.subheader("📜 Mural de Oportunidades (Global)")
if alerts_history:
    for alert in alerts_history:
        st.markdown(f"**{alert['source_name']}** - `{alert['found_keywords']}`")