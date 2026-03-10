import yfinance as yf
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os

def get_market_recap():
    api_key = os.environ.get('NEWS_API_KEY')
    # Fetch headlines about the stock market from the last 7 days
    url = f'https://newsapi.org/v2/everything?q=stock+market+recap&language=en&sortBy=relevancy&apiKey={api_key}'
    response = requests.get(url).json()
    
    recap = "\n📰 WEEKLY MARKET RECAP HEADLINES\n"
    if response.get('status') == 'ok':
        articles = response['articles'][:3] # Get top 3 headlines
        for art in articles:
            recap += f"- {art['title']}\n  (Source: {art['source']['name']})\n"
    return recap

def get_winners_losers():
    # Influential stocks for S&P 500, FTSE, and DAX
    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "SHEL.L", "BP.L", "SAP.DE", "SIE.DE"]
    data = []
    
    for symbol in tickers:
        t = yf.Ticker(symbol)
        hist = t.history(period="5d") # 5-day performance
        if len(hist) >= 2:
            change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            data.append({'symbol': symbol, 'change': change})
            
    sorted_data = sorted(data, key=lambda x: x['change'], reverse=True)
    return sorted_data[:3], sorted_data[-3:]

def build_report():
    winners, losers = get_winners_losers()
    recap = get_market_recap()
    
    report = f"Market Intelligence Deep Dive: {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "="*50 + "\n"
    
    report += "\n🚀 TOP 3 WINNERS OF THE WEEK\n"
    for w in winners: report += f"  {w['symbol']}: {w['change']:+.2f}%\n"
    
    report += "\n📉 BOTTOM 3 LOSERS OF THE WEEK\n"
    for l in losers: report += f"  {l['symbol']}: {l['change']:+.2f}%\n"
    
    report += recap
    return report

def send_email(content):
    msg = MIMEText(content)
    msg['Subject'] = f"Weekly Intelligence Recap - {datetime.now().strftime('%d %b')}"
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('EMAIL_RECEIVER')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
        server.send_message(msg)

if __name__ == "__main__":
    report_content = build_report()
    send_email(report_content)
    print("Deep recap sent successfully!")
