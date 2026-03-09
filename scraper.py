import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def log_to_supabase(source, keywords, url):
    sb_url = os.environ.get("SUPABASE_URL")
    sb_key = os.environ.get("SUPABASE_KEY")
    if sb_url and sb_key:
        sb: Client = create_client(sb_url, sb_key)
        sb.table("alert_history").insert({
            "source_name": source,
            "found_keywords": ", ".join(keywords),
            "url": url
        }).execute()

def check_multiple_sources():
    targets = [
        {"name": "MS Training Days (Global)", "url": "https://events.microsoft.com/en-us/allevents/"},
        {"name": "Microsoft Learn Challenges", "url": "https://learn.microsoft.com/en-us/credentials/certifications/challenges"},
        {"name": "Mindhub (Discounts)", "url": "https://www.mindhub.com/microsoft-certification-exam-vouchers"}
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    found_opportunities = []

    for site in targets:
        try:
            response = requests.get(site['url'], headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                content = soup.get_text().lower()
                
                keywords = [
                    "free", "gratuito", "grátis", "100% off", "zero cost", "no-cost", 
                    "discount", "desconto", "voucher", "promo", "off", "coupon", "cupom",
                    "50% off", "30% off", "exam replay",
                    "az-900", "sc-900", "sc-300", "az-104", "microsoft learn", "cloud skills challenge"
                ]
                                
                matches = [word for word in keywords if word in content]
                if matches:
                    found_opportunities.append(f"✅ {site['name']}: {', '.join(set(matches))}")
                    # Logando no banco de dados apenas quando houver achados
                    log_to_supabase(site['name'], list(set(matches)), site['url'])
        except Exception as e:
            print(f"Erro ao varrer {site['name']}: {e}")

    return found_opportunities

def send_telegram_alert(message):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": message})

def run_watcher():
    opps = check_multiple_sources()
    if opps:
        msg = "🚨 NOVAS OPORTUNIDADES DETECTADAS!\n\n" + "\n".join(opps)
        send_telegram_alert(msg)
        return {"status": "Success", "details": opps}
    return {"status": "No new deals", "details": []}

if __name__ == "__main__":
    run_watcher()