import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import requests

# 1. Configurações de Segurança
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Cert-Manager Pro", page_icon="🚀", layout="wide")

# 2. Funções de Dados
def get_certifications():
    response = supabase.table("certifications").select("*").order("id").execute()
    return response.data

def get_dollar_rate():
    try:
        res = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()
        return float(res['USDBRL']['bid'])
    except:
        return 5.10

# 3. Interface Visual
st.title("🚀 Cert-Manager: Roadmap Pleno")

dolar = get_dollar_rate()
certs = get_certifications()

# Métricas no Topo
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Cotação USD/BRL", f"R$ {dolar:.2f}")
with col2:
    st.metric("Próximo Desafio", "AZ-900")
with col3:
    st.metric("Foco Carreira", "Identity & Security")

st.write("---")

# Exibição da Trilha
st.subheader("🎯 Minha Trilha Microsoft")

for cert in certs:
    with st.expander(f"{cert['name']} - {cert['status']}"):
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"**Categoria:** {cert['category']}")
        c2.write(f"**Preço USD:** ${cert['price_usd']}")
        
        # Cálculo em tempo real usando a cotação da API
        price_brl = float(cert['price_usd']) * dolar
        c3.write(f"**Preço BRL:** R$ {price_brl:.2f}")
        
        if cert['name'] == 'SC-300':
            st.info("💡 Foco especial: Essencial para o projeto de reestruturação de AD.")