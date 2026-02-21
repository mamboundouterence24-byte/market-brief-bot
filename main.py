import yfinance as yf
import pandas as pd
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIGURATION ---
# These pull from your GitHub Secrets (EMAIL_USER and EMAIL_PASS)
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

def get_sp500_movers():
    print("🚀 Fetching S&P 500 Tickers...")
    import requests
    
    # We add a 'User-Agent' so Wikipedia knows we are a real browser
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    table = pd.read_html(response.text)[0]
    tickers = table['Symbol'].tolist()
    
    # Clean tickers (some have dots like BRK.B which Yahoo prefers as BRK-B)
    tickers = [t.replace('.', '-') for t in tickers]
    
    print(f"📊 Analyzing {len(tickers)} companies...")
    
    # Download data
    data = yf.download(tickers, period="5d", interval="1d", group_by='ticker', threads=True)
    
    performance = []
    for ticker in tickers:
        try:
            df = data[ticker]
            if not df.empty and len(df) >= 2:
                start_price = df['Close'].iloc[0]
                end_price = df['Close'].iloc[-1]
                pct_change = ((end_price - start_price) / start_price) * 100
                
                performance.append({
                    'Ticker': ticker,
                    'Price': end_price,
                    'Change': pct_change
                })
        except:
            continue

    perf_df = pd.DataFrame(performance)
    top_10 = perf_df.nlargest(10, 'Change')
    bottom_10 = perf_df.nsmallest(10, 'Change')
    
    return top_10, bottom_10

def build_html_report(top, bot):
    now = datetime.now().strftime('%Y-%m-%d')
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2c3e50;">Market Intelligence Report: {now}</h2>
        <p>This report identifies the biggest movers in the S&P 500 over the last 5 trading days.</p>
        
        <h3 style="color: #27ae60;">🚀 Top 10 Winners</h3>
        <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th>Ticker</th><th>Price</th><th>Weekly Change</th>
            </tr>
    """
    for _, row in top.iterrows():
        html += f"<tr><td><b>{row['Ticker']}</b></td><td>${row['Price']:.2f}</td><td style='color:green;'>+{row['Change']:.2f}%</td></tr>"
        
    html += """
        </table>
        <br>
        <h3 style="color: #c0392b;">📉 Top 10 Losers</h3>
        <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th>Ticker</th><th>Price</th><th>Weekly Change</th>
            </tr>
    """
    for _, row in bot.iterrows():
        html += f"<tr><td><b>{row['Ticker']}</b></td><td>${row['Price']:.2f}</td><td style='color:red;'>{row['Change']:.2f}%</td></tr>"
        
    html += """
        </table>
        <p style="font-size: 10px; color: grey;">Generated automatically via GitHub Actions.</p>
    </body>
    </html>
    """
    return html

def send_email(content):
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ Error: Missing EMAIL_USER or EMAIL_PASS secrets!")
        return

    msg = MIMEMultipart()
    msg['Subject'] = f"Weekly Market Intelligence - {datetime.now().strftime('%b %d')}"
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER # Sending to yourself
    
    msg.attach(MIMEText(content, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print("✅ SUCCESS: Intelligence report sent!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# --- EXECUTION ---
if __name__ == "__main__":
    winners, losers = get_sp500_movers()
    report_content = build_html_report(winners, losers)
    send_email(report_content)

