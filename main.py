import yfinance as yf
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

def get_market_intelligence():
    # 1. Fetch Global Indices (The "Must-Have" Section)
    indices = {"S&P 500": "^GSPC", "FTSE 100": "^FTSE", "DAX 40": "^GDAXI"}
    report = f"Market Intelligence Report: {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "="*50 + "\n\n"
    report += "📊 GLOBAL INDICES\n"
    
    for name, sym in indices.items():
        idx = yf.Ticker(sym)
        h = idx.history(period="2d")
        if len(h) >= 2:
            change = ((h['Close'].iloc[-1] - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
            report += f"{name}: {h['Close'].iloc[-1]:,.2f} ({change:+.2f}% Today)\n"

    # 2. Fetch Top 5 Winners & Losers (The "Deep Dive" Section)
    # Using key global bellwethers for a representative sample
    stocks = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "LLY", "V", "SHEL.L", "BP.L", "SAP.DE", "SIE.DE", "AIR.PA"]
    data = []
    for symbol in stocks:
        t = yf.Ticker(symbol)
        hist = t.history(period="5d")
        if len(hist) >= 2:
            w_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            data.append({'symbol': symbol, 'change': w_change})
    
    sorted_stocks = sorted(data, key=lambda x: x['change'], reverse=True)
    
    report += "\n🚀 TOP 5 WEEKLY WINNERS\n"
    for w in sorted_stocks[:5]: report += f"  {w['symbol']}: {w['change']:+.2f}%\n"
    
    report += "\n📉 BOTTOM 5 WEEKLY LOSERS\n"
    for l in sorted_stocks[-5:]: report += f"  {l['symbol']}: {l['change']:+.2f}%\n"

    # 3. Professional News Recap (Filtering for Quality)
    api_key = os.environ.get('NEWS_API_KEY')
    domains = "reuters.com,bloomberg.com,wsj.com,cnbc.com,ft.com"
    url = f'https://newsapi.org/v2/everything?domains={domains}&q=finance&sortBy=publishedAt&apiKey={api_key}'
    
    try:
        response = requests.get(url).json()
        report += "\n📰 PROFESSIONAL MARKET HEADLINES\n"
        if response.get('status') == 'ok':
            for art in response['articles'][:5]:
                report += f"- {art['title']} ({art['source']['name']})\n"
    except:
        report += "\n(Professional news feed temporarily unavailable)\n"

    return report

def send_email(content):
    msg = MIMEText(content)
    msg['Subject'] = f"Weekly Market Deep Dive - {datetime.now().strftime('%d %b')}"
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('EMAIL_RECEIVER')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
        server.send_message(msg)

if __name__ == "__main__":
    content = get_market_intelligence()
    send_email(content)
    print("Full intelligence report sent!")
