import yfinance as yf
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from newsapi import NewsApiClient

# --- CONFIGURATION ---
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
RECEIVER_EMAIL = "mamboundouterence24@gmail.com"

# Indices and Stock Watchlist
INDICES = {"S&P 500": "^GSPC", "FTSE 100": "^FTSE", "DAX 40": "^GDAXI"}
WATCHLIST = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "BRK-B", "LLY", "BP.L", "SHEL.L", "SAP.DE", "SIE.DE"]

def get_weekly_stats(symbol):
    """Calculates price and % change from Monday Open to Friday Close."""
    ticker = yf.Ticker(symbol)
    # period="5d" captures the Monday-Friday trading window
    hist = ticker.history(period="5d")
    
    if len(hist) < 2:
        return 0.0, 0.0
    
    monday_open = hist['Open'].iloc[0]
    friday_close = hist['Close'].iloc[-1]
    weekly_perf = ((friday_close - monday_open) / monday_open) * 100
    
    return friday_close, weekly_perf

def get_market_news():
    """Fetches professional headlines via NewsAPI."""
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    top_headlines = newsapi.get_top_headlines(
        sources='bloomberg,reuters,the-wall-street-journal,fortune,business-insider',
        language='en'
    )
    articles = top_headlines.get('articles', [])
    return [f"- {a['title']} ({a['source']['name']})" for a in articles[:5]]

# --- DATA PROCESSING ---
report_date = datetime.now().strftime("%Y-%m-%d")
body = f"Market Intelligence Report: {report_date} (Weekly Review)\n"
body += "="*40 + "\n\n"

# 1. Global Indices
body += "📊 GLOBAL INDICES (Weekly Perf)\n"
for name, sym in INDICES.items():
    price, perf = get_weekly_stats(sym)
    body += f"{name}: {price:,.2f} ({perf:+.2f}% This Week)\n"

# 2. Stock Performance Sorting
all_stats = []
for stock in WATCHLIST:
    _, perf = get_weekly_stats(stock)
    all_stats.append({'symbol': stock, 'perf': perf})

# Filter: Winners must be > 0%, Losers must be < 0%
winners = sorted([s for s in all_stats if s['perf'] > 0], key=lambda x: x['perf'], reverse=True)[:5]
losers = sorted([s for s in all_stats if s['perf'] < 0], key=lambda x: x['perf'])[:5]

body += "\n🚀 TOP 5 WEEKLY WINNERS\n"
if not winners:
    body += "No positive gainers this week.\n"
for w in winners:
    body += f"{w['symbol']}: {w['perf']:+.2f}%\n"

body += "\n📉 BOTTOM 5 WEEKLY LOSERS\n"
for l in losers:
    body += f"{l['symbol']}: {l['perf']:+.2f}%\n"

# 3. News Headlines
body += "\n📰 PROFESSIONAL MARKET HEADLINES\n"
headlines = get_market_news()
body += "\n".join(headlines)

# --- SEND EMAIL ---
msg = EmailMessage()
msg.set_content(body)
msg['Subject'] = f"Weekly Market Briefing - {report_date}"
msg['From'] = EMAIL_USER
msg['To'] = RECEIVER_EMAIL

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print("Report sent successfully!")
except Exception as e:
    print(f"Error: {e}")
