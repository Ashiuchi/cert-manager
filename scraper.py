from scraper import check_microsoft_offers

st.write("---")
st.subheader("🔍 Web Watcher: Monitor de Descontos")

if st.button("Executar Varredura por Vouchers"):
    with st.spinner("Vasculhando sites oficiais da Microsoft..."):
        result = check_microsoft_offers()
        
        if result["status"] == "Success":
            st.success(f"🚨 Possíveis oportunidades encontradas para: {', '.join(result['offers'])}")
            st.info(f"Verifique os detalhes em: {result['url']}")
        elif result["status"] == "No offers found":
            st.warning("Nenhum voucher direto detectado hoje. Continue focado nos estudos!")
        else:
            st.error(f"Erro ao acessar o monitor: {result['message']}")