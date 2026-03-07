import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

def get_market_data():
    # Tickers for S&P 500, FTSE 100, and DAX
    tickers = {"S&P 500": "^GSPC", "FTSE 100": "^FTSE", "DAX 40": "^GDAXI"}
    report = f"Market Briefing: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    for name, symbol in tickers.items():
        ticker = yf.Ticker(symbol)
        # Get the most recent 2 days to calculate change
        hist = ticker.history(period="2d")
        
        if len(hist) >= 2:
            close_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            pct_change = ((close_price - prev_close) / prev_close) * 100
            
            direction = "▲" if pct_change >= 0 else "▼"
            report += f"{name}: {close_price:,.2f} ({direction} {pct_change:.2f}%)\n"
        else:
            report += f"{name}: Data currently unavailable\n"
            
    return report

def send_email(content):
    msg = MIMEText(content)
    msg['Subject'] = f"Market Update - {datetime.now().strftime('%d %b %Y')}"
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('EMAIL_RECEIVER')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
        server.send_message(msg)

if __name__ == "__main__":
    market_report = get_market_data()
    send_email(market_report)
    print("Report sent successfully!")
