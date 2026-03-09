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

# --- FUNÇÕES DE AUTENTICAÇÃO ---
def login_user(username, password):
    res = supabase.table("app_users").select("*").eq("username", username).eq("password", password).execute()
    return res.data if res.data else None

def register_user(username, password, question, answer):
    try:
        supabase.table("app_users").insert({
            "username": username, 
            "password": password, 
            "security_question": question, 
            "security_answer": answer
        }).execute()
        return True
    except: return False

def reset_password(username, answer, new_password):
    # Valida se a resposta de segurança bate
    user_check = supabase.table("app_users").select("*").eq("username", username).eq("security_answer", answer).execute()
    if user_check.data:
        supabase.table("app_users").update({"password": new_password}).eq("username", username).execute()
        return True
    return False

# Gerenciamento de Sessão
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user'] = None

# --- TELA DE ACESSO ---
if not st.session_state['logged_in']:
    st.title("🔐 Cert-Manager: Acesso")
    tab_l, tab_r, tab_f = st.tabs(["Entrar", "Criar Conta", "Esqueci Senha"])
    
    with tab_l:
        u_in = st.text_input("Usuário", key="login_u")
        p_in = st.text_input("Senha", type="password", key="login_p")
        if st.button("Acessar Dashboard"):
            if login_user(u_in, p_in):
                st.session_state['logged_in'], st.session_state['user'] = True, u_in
                st.rerun()
            else: st.error("Credenciais inválidas.")

    with tab_r:
        st.subheader("Novo Cadastro")
        nu = st.text_input("Nome de Usuário")
        np = st.text_input("Senha", type="password")
        sq = st.selectbox("Pergunta de Segurança", [
            "Qual o nome do seu primeiro pet?",
            "Qual a sua cidade natal?",
            "Qual o modelo do seu primeiro carro?",
            "Qual o nome da sua primeira escola?"
        ])
        sa = st.text_input("Sua Resposta (Lembre-se dela!)")
        if st.button("Registrar Conta"):
            if nu and np and sa:
                if register_user(nu, np, sq, sa): st.success("Conta criada! Pode logar.")
                else: st.error("Erro: Usuário já existe.")
            else: st.warning("Preencha todos os campos.")

    with tab_f:
        st.subheader("Recuperar Acesso")
        ru = st.text_input("Seu Usuário", key="reset_u")
        # Busca a pergunta se o usuário for digitado
        if ru:
            user_q = supabase.table("app_users").select("security_question").eq("username", ru).execute()
            if user_q.data:
                st.info(f"Pergunta: {user_q.data[0]['security_question']}")
                ra = st.text_input("Sua Resposta", key="reset_a")
                rn = st.text_input("Nova Senha", type="password", key="reset_n")
                if st.button("Redefinir Senha"):
                    if reset_password(ru, ra, rn): st.success("Senha alterada com sucesso!")
                    else: st.error("Resposta de segurança incorreta.")
            else: st.error("Usuário não encontrado.")
    st.stop()

# --- DASHBOARD (APÓS LOGIN) ---
user = st.session_state['user']
st.title(f"🚀 Dashboard de {user}")
if st.sidebar.button("🚪 Sair"):
    st.session_state['logged_in'] = False
    st.rerun()

# (Restante do código de métricas, roadmap e scraper que já temos...)
# 2. Funções de Backend
def get_dashboard_data(user_name):
    certs = supabase.table("certifications").select("*").order("id").execute()
    wallet = supabase.table("study_wallet").select("balance_brl").eq("user_name", user_name).order("id", desc=True).limit(1).execute()
    history = supabase.table("alert_history").select("*").order("alert_date", desc=True).limit(5).execute()
    links = supabase.table("cert_links").select("*").eq("user_name", user_name).execute()
    progress = supabase.table("user_progress").select("*").eq("user_name", user_name).execute()
    
    balance = float(wallet.data[0]['balance_brl']) if wallet.data else 0.0
    return certs.data, balance, history.data, links.data, progress.data

def get_dollar_rate():
    try:
        res = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()
        return float(res['USDBRL']['bid'])
    except: return 5.15

dolar = get_dollar_rate()
certs, current_balance, alerts_history, all_links, user_progress = get_dashboard_data(user)

m1, m2, m3 = st.columns(3)
m1.metric("Cotação USD/BRL", f"R$ {dolar:.2f}")
m2.metric("Seu Saldo", f"R$ {current_balance:.2f}")
m3.metric("Foco", "Cloud & Security")

# Sidebar - Ações
st.sidebar.header("⚙️ Painel de Controle")
with st.sidebar.form("deposit_form"):
    deposit = st.number_input("Novo aporte (R$):", min_value=0.0, step=50.0)
    if st.form_submit_button("Confirmar Depósito"):
        supabase.table("study_wallet").insert({"balance_brl": current_balance + deposit, "user_name": user}).execute()
        st.rerun()

# 5. Roadmap
st.subheader("🎯 Suas Trilhas")
for cert in certs:
    price_brl = float(cert['price_usd']) * dolar
    progress_fin = min(current_balance / price_brl, 1.0) if price_brl > 0 else 0
    
    with st.expander(f"📌 {cert['name']} - {cert['status']}"):
        col_info, col_lab = st.columns([1, 1.5])
        
        with col_info:
            st.markdown("#### 💰 Financeiro")
            st.progress(progress_fin)
            
            cert_links = [l for l in all_links if l['cert_id'] == cert['id']]
            for l in cert_links: st.link_button(f"📄 {l['link_name']}", l['url'])
            
            with st.popover("➕ Adicionar"):
                n = st.text_input("Nome", key=f"n_{cert['id']}")
                u = st.text_input("URL", key=f"u_{cert['id']}")
                if st.button("Salvar", key=f"b_{cert['id']}"):
                    supabase.table("cert_links").insert({"cert_id": cert['id'], "link_name": n, "url": u, "user_name": user}).execute()
                    st.rerun()

        with col_lab:
            st.markdown(f"#### 🧪 Lab Guide")
            if cert.get('lab_guide'):
                lines = cert['lab_guide'].split('\n')
                tasks = [line.replace('- [ ]', '').strip() for line in lines if line.startswith('- [ ]')]
                completed = 0
                for i, t in enumerate(tasks):
                    is_done = any(p['cert_id'] == cert['id'] and p['task_index'] == i and p['is_completed'] for p in user_progress)
                    if st.checkbox(t, value=is_done, key=f"chk_{user}_{cert['id']}_{i}"):
                        completed += 1
                        if not is_done: supabase.table("user_progress").upsert({"user_name": user, "cert_id": cert['id'], "task_index": i, "is_completed": True}).execute()
                    elif is_done: supabase.table("user_progress").upsert({"user_name": user, "cert_id": cert['id'], "task_index": i, "is_completed": False}).execute()
                st.progress(completed / len(tasks) if tasks else 0)

# 6. Histórico Global
st.write("---")
st.subheader("📜 Mural de Oportunidades")
if alerts_history:
    for a in alerts_history:
        st.markdown(f"**{a['source_name']}** - `{a['found_keywords']}`")