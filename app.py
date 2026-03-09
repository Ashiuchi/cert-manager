import streamlit as st
import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from scraper import run_watcher # Importando sua automação consolidada

# 1. Configurações de Ambiente e Segurança
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
    """Busca certificações, saldo e histórico de alertas."""
    certs = supabase.table("certifications").select("*").order("id").execute()
    wallet = supabase.table("study_wallet").select("balance_brl").order("id", desc=True).limit(1).execute()
    history = supabase.table("alert_history").select("*").order("alert_date", desc=True).limit(5).execute()
    
    balance = float(wallet.data[0]['balance_brl']) if wallet.data else 0.0
    return certs.data, balance, history.data

def get_dollar_rate():
    """Monitoramento em tempo real da cotação USD/BRL."""
    try:
        res = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()
        return float(res['USDBRL']['bid'])
    except:
        return 5.15 # Fallback atualizado

# 3. Processamento Inicial
dolar = get_dollar_rate()
certs, current_balance, alerts_history = get_dashboard_data()

# 4. Interface do Usuário (UI)
st.title("🚀 Cert-Manager: Roadmap Pleno")

# Métricas Principais
m1, m2, m3 = st.columns(3)
m1.metric("Cotação USD/BRL", f"R$ {dolar:.2f}")
m2.metric("Saldo em Carteira", f"R$ {current_balance:.2f}")
m3.metric("Foco Carreira", "Identity & Security (SC-300)")

st.write("---")

# Sidebar: Aportes e Execução Manual do Scraper
st.sidebar.header("⚙️ Painel de Controle")

with st.sidebar.form("deposit_form"):
    deposit = st.number_input("Novo aporte (R$):", min_value=0.0, step=50.0)
    if st.form_submit_button("Confirmar Depósito"):
        new_total = current_balance + deposit
        supabase.table("study_wallet").insert({"balance_brl": new_total}).execute()
        st.success("Saldo atualizado!")
        st.rerun()

st.sidebar.write("---")
if st.sidebar.button("🔍 Executar Varredura Global"):
    with st.sidebar.status("Varrendo múltiplas fontes..."):
        result = run_watcher()
        if result["status"] == "Success":
            st.sidebar.success("Novas oportunidades detectadas e enviadas ao Telegram!")
            st.rerun()
        else:
            st.sidebar.info("Nenhuma oferta nova encontrada no momento.")

# 5. Roadmap e Progresso Financeiro
st.subheader("🎯 Minha Trilha Microsoft")

for cert in certs:
    price_brl = float(cert['price_usd']) * dolar
    progress = min(current_balance / price_brl, 1.0) if price_brl > 0 else 0
    
    with st.expander(f"📌 {cert['name']} - {cert['status']}"):
        col_info, col_prog = st.columns([1, 2])
        
        with col_info:
            st.write(f"**Categoria:** {cert['category']}")
            st.write(f"**Investimento:** R$ {price_brl:.2f}")
            if cert.get('exam_url'):
                st.link_button("Ir para o MS Learn", cert['exam_url'])
        
        with col_prog:
            st.write(f"**Progresso de Poupança:** {progress*100:.1f}%")
            st.progress(progress)
            if progress >= 1.0:
                st.success("✅ Valor disponível para agendamento!")
            else:
                st.caption(f"Faltam R$ {price_brl - current_balance:.2f}")
                
st.write("---")
st.subheader("📚 Central de Estudos: Microsoft Learn")

# Criando abas para organizar o material
tab1, tab2, tab3 = st.tabs(["Material SC-300", "Material AZ-900", "Anotações Rápidas"])

with tab1:
    st.markdown("### 🔐 Foco: Identity and Access Administrator")
    st.write("Link direto para o roteiro oficial:")
    st.link_button("Abrir Trilha SC-300 no MS Learn", "https://learn.microsoft.com/en-us/training/courses/sc-300t00")
    
    # Exemplo de incorporação (Note: alguns sites da MS podem bloquear exibição em iframe por segurança)
    st.info("💡 Dica: Use esta seção para salvar os links dos módulos de AD que você está aplicando no SFB.")

with tab2:
    st.markdown("### ☁️ Foco: Azure Fundamentals")
    st.write("Material base para a certificação inicial:")
    st.link_button("Abrir roteiro AZ-900", "https://learn.microsoft.com/en-us/training/paths/microsoft-azure-fundamentals-cloud-concepts/")

with tab3:
    st.markdown("### 📝 Meu 'Cheat Sheet' (Comandos Úteis)")
    # Espaço para você listar os comandos de PowerShell que mais usa no Serviço Florestal
    with st.expander("Comandos de PowerShell para AD"):
        st.code("""
# Listar usuários de uma Unidade Organizacional (OU)
Get-ADUser -Filter * -SearchBase "OU=Usuarios,DC=sfb,DC=gov,DC=br"

# Verificar membros de um grupo de segurança
Get-ADGroupMember -Identity "Grupo_Seguranca_Financeiro"
        """, language="powershell")

# 6. Histórico de Oportunidades (Web Watcher)
st.write("---")
st.subheader("📜 Últimas Oportunidades Detectadas")

if alerts_history:
    for alert in alerts_history:
        with st.container():
            date_fmt = alert['alert_date'][:10]
            st.markdown(f"**{date_fmt} - {alert['source_name']}**")
            st.write(f"Achados: `{alert['found_keywords']}`")
            st.link_button(f"Verificar em {alert['source_name']}", alert['url'])
            st.write("")
else:
    st.info("O histórico está vazio. Execute uma varredura para começar.")