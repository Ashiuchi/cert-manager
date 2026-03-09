import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Carrega variáveis locais se existirem
load_dotenv()

def send_telegram_alert(message):
    """
    Envia alertas em tempo real para o seu Telegram.
    Essencial para monitoramento proativo de carreira.
    """
    # Busca tokens do ambiente (Local ou Streamlit Secrets)
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
        except Exception as e:
            print(f"Erro ao enviar alerta: {e}")

def check_microsoft_offers():
    """
    Realiza a varredura no hub de treinamentos da Microsoft.
    Foco: Vouchers para AZ-900, SC-900, SC-300 e AZ-104.
    """
    url = "https://www.microsoft.com/pt-br/trainingdays"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text().lower()
        
        # Sua trilha estratégica de ascensão para Pleno
        keywords = ["az-900", "sc-900", "sc-300", "az-104", "voucher", "gratuito", "free"]
        found = [word for word in keywords if word in content]
        
        if found:
            results = f"🚨 VOUCHER/TREINAMENTO DETECTADO!\nO Cert-Manager encontrou oportunidades para: {', '.join(set(found))}.\nConfira em: {url}"
            send_telegram_alert(results)
            return {"status": "Success", "offers": list(set(found)), "url": url}
        
        return {"status": "No offers found", "offers": [], "url": url}
        
    except Exception as e:
        error_msg = f"Erro na varredura: {str(e)}"
        print(error_msg)
        return {"status": "Error", "message": error_msg}

# Permite execução manual para teste ou via GitHub Actions
if __name__ == "__main__":
    print("Iniciando varredura manual...")
    resultado = check_microsoft_offers()
    print(f"Resultado: {resultado['status']}")