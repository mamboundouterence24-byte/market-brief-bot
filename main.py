import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

def get_winners_losers(ticker_list):
    data = []
    # Download 1 week of data for comparison
    for symbol in ticker_list:
        t = yf.Ticker(symbol)
        hist = t.history(period="5d")
        if len(hist) >= 2:
            change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            data.append({'symbol': symbol, 'change': change})
    
    # Sort and pick top 3 for each
    sorted_data = sorted(data, key=lambda x: x['change'], reverse=True)
    return sorted_data[:3], sorted_data[-3:]

def get_market_intelligence():
    indices = {"S&P 500": "^GSPC", "FTSE 100": "^FTSE", "DAX 40": "^GDAXI"}
    # Top influential stocks for each index
    sp500_stocks = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B"]
    ftse_stocks = ["SHEL.L", "AZN.L", "HSBA.L", "ULVR.L", "BP.L", "GSK.L", "RIO.L"]
    
    report = f"Market Intelligence Report: {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "="*40 + "\n\n"

    for name, sym in indices.items():
        idx = yf.Ticker(sym)
        h = idx.history(period="5d")
        weekly_chg = ((h['Close'].iloc[-1] - h['Close'].iloc[0]) / h['Close'].iloc[0]) * 100
        report += f"{name}: {h['Close'].iloc[-1]:,.2f} ({weekly_chg:+.2f}% this week)\n"
    
    report += "\n🚀 TOP WEEKLY MOVERS (S&P 500 Sample)\n"
    winners, losers = get_winners_losers(sp500_stocks)
    for w in winners: report += f"  {w['symbol']}: {w['change']:+.2f}%\n"
    report += "\n📉 BOTTOM WEEKLY MOVERS (S&P 500 Sample)\n"
    for l in losers: report += f"  {l['symbol']}: {l['change']:+.2f}%\n"

    return report

def send_email(content):
    msg = MIMEText(content)
    msg['Subject'] = f"Weekly Market Intelligence - {datetime.now().strftime('%d %b')}"
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('EMAIL_RECEIVER')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
        server.send_message(msg)

if __name__ == "__main__":
    content = get_market_intelligence()
    send_email(content)
    print("Intelligence report sent!")
