import streamlit as st
import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Configurações de Ambiente e Segurança
load_dotenv()
url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not url or not key:
    st.error("Erro: Credenciais do Supabase não encontradas.")
    st.stop()

supabase: Client = create_client(url, key)

st.set_page_config(page_title="Cert-Manager Pro", page_icon="🚀", layout="wide")

# 2. Funções de Backend (Consolidadas)
def get_data():
    """Busca certificações e saldo da carteira simultaneamente."""
    certs = supabase.table("certifications").select("*").order("id").execute()
    wallet = supabase.table("study_wallet").select("balance_brl").order("id", desc=True).limit(1).execute()
    balance = float(wallet.data[0]['balance_brl']) if wallet.data else 0.0
    return certs.data, balance

def get_dollar_rate():
    """Monitoramento em tempo real da cotação USD/BRL."""
    try:
        res = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()
        return float(res['USDBRL']['bid'])
    except:
        return 5.10 # Valor de segurança (fallback)

# 3. Processamento de Dados
dolar = get_dollar_rate()
certs, current_balance = get_data()

# 4. Interface do Usuário (UI)
st.title("🚀 Cert-Manager: Roadmap Pleno")

# Dashboard de Métricas
m1, m2, m3 = st.columns(3)
m1.metric("Cotação USD/BRL", f"R$ {dolar:.2f}")
m2.metric("Saldo em Carteira", f"R$ {current_balance:.2f}")
m3.metric("Foco Atual", "AZ-900 & SC-300")

st.write("---")

# Sidebar para Aportes Financeiros
st.sidebar.header("💰 Gestão Financeira")
with st.sidebar.form("deposit_form"):
    deposit = st.number_input("Novo aporte para estudos (R$):", min_value=0.0, step=50.0)
    if st.form_submit_button("Confirmar Depósito"):
        new_total = current_balance + deposit
        supabase.table("study_wallet").insert({"balance_brl": new_total}).execute()
        st.success("Depósito realizado com sucesso!")
        st.rerun()

# 5. Roadmap e Progresso Financeiro
st.subheader("🎯 Minha Trilha Microsoft")

for cert in certs:
    price_usd = float(cert['price_usd'])
    price_brl = price_usd * dolar
    
    # Cálculo de progresso baseado no saldo atual
    progress = min(current_balance / price_brl, 1.0) if price_brl > 0 else 0
    
    with st.expander(f"📌 {cert['name']} - {cert['status']}"):
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.write(f"**Categoria:** {cert['category']}")
            st.write(f"**Custo:** ${price_usd:.2f} (R$ {price_brl:.2f})")
        
        with c2:
            st.write(f"**Progresso Financeiro:** {progress*100:.1f}%")
            st.progress(progress)
            
            if progress >= 1.0:
                st.success("✅ Recurso disponível para o voucher!")
            else:
                st.info(f"Faltam R$ {price_brl - current_balance:.2f} para atingir a meta.")

        # Link oficial para monitoramento manual (até o scraper estar pronto)
        if cert.get('exam_url'):
            st.link_button("Ver no Microsoft Learn", cert['exam_url'])