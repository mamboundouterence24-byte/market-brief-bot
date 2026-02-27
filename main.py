import os
import smtplib
import pandas as pd
import requests
from io import StringIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def get_market_data():
    """Fetches tickers and basic info for the requested indices."""
    results = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 1. S&P 500 from Wikipedia
    try:
        url_sp = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        resp_sp = requests.get(url_sp, headers=headers)
        df_sp = pd.read_html(StringIO(resp_sp.text))[0]
        results.append(f"S&P 500: {len(df_sp)} companies listed.")
    except Exception as e:
        results.append(f"S&P 500 Fetch Error: {e}")

    # 2. FTSE 100 
    try:
        url_ftse = 'https://en.wikipedia.org/wiki/FTSE_100_Index'
        resp_ftse = requests.get(url_ftse, headers=headers)
        df_ftse = pd.read_html(StringIO(resp_ftse.text))[3] # Table index may vary
        results.append(f"FTSE 100: {len(df_ftse)} companies listed.")
    except Exception as e:
        results.append(f"FTSE 100 Fetch Error: {e}")

    # 3. DAX 40 (Formerly DAX 30)
    try:
        url_dax = 'https://en.wikipedia.org/wiki/DAX'
        resp_dax = requests.get(url_dax, headers=headers)
        df_dax = pd.read_html(StringIO(resp_dax.text))[4]
        results.append(f"DAX 40: {len(df_dax)} companies listed.")
    except Exception as e:
        results.append(f"DAX Fetch Error: {e}")

    return "\n".join(results)

def send_email(content):
    sender_email = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')
    receiver_email = "mamboundouterence24@gmail.com"

    if not sender_email or not password:
        print("❌ Error: EMAIL_USER or EMAIL_PASS secrets are missing!")
        return

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"Market Briefing: {datetime.now().strftime('%Y-%m-%d')}"

    body = f"Hello,\n\nHere is your market update for the S&P 500, FTSE 100, and DAX:\n\n{content}\n\nBest regards,\nYour Market Bot"
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    print("🚀 Starting Market Report...")
    report_data = get_market_data()
    send_email(report_data)
