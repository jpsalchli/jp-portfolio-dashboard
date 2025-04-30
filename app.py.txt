import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import requests
from datetime import datetime

# Title
st.set_page_config(layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

# Portfolio
portfolio = {
    "Ticker": ["FNV", "CFR.SW", "NOVO-B.CO", "NDA-FI.HE", "LLY", "AXON", "KD", "VWCE.DE", "VYM", "GRMNY"],
    "Company": [
        "Franco Nevada", "Richemont", "Novo Nordisk", "Nordea Bank",
        "Eli Lilly", "Axon Enterprise", "Kyndryl Holdings",
        "Vanguard FTSE All World", "Vanguard High Dividend", "Chimera Germany ETF"]
}
df = pd.DataFrame(portfolio)

# API key for Finnhub
FINNHUB_TOKEN = "d08j1rpr01qju5m6q6d0d08j1rpr01qju5m6q6dg"

def get_finnhub_sentiment(ticker):
    try:
        url = f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={FINNHUB_TOKEN}"
        r = requests.get(url)
        if r.status_code == 200:
            score = r.json().get("companyNewsScore", None)
            if score is None:
                return "Not Available"
            elif score > 0.1:
                return "Positive"
            elif score < -0.1:
                return "Negative"
            else:
                return "Neutral"
        return "Not Available"
    except:
        return "Not Available"

def get_finnhub_news(ticker):
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from=2024-01-01&to=2025-12-31&token={FINNHUB_TOKEN}"
        r = requests.get(url)
        articles = r.json()[:5]
        return articles
    except:
        return []

# Sidebar for ticker selection
ticker = st.sidebar.selectbox("Select a stock:", df["Ticker"])
company = df[df["Ticker"] == ticker]["Company"].values[0]

# Stock info
st.subheader(f"{company} ({ticker})")
try:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")
    if hist.empty:
        st.warning("No price data available.")
    else:
        latest_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else latest_price
        change = ((latest_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Price (USD)", f"{latest_price:.2f}")
        col2.metric("Change (%)", f"{change:.2f}%", delta_color="inverse")
        col3.metric("Sentiment", get_finnhub_sentiment(ticker))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode='lines', name='Close'))
        fig.update_layout(title=f"{ticker} Price Chart (6mo)", xaxis_title="Date", yaxis_title="USD", height=400)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load stock data: {e}")

# News headlines
st.markdown("### 📰 Latest News")
news_items = get_finnhub_news(ticker)
if not news_items:
    st.info("No recent news available.")
else:
    for item in news_items:
        st.markdown(f"- **{item['headline']}** ({item['source']}, {datetime.fromtimestamp(item['datetime']).date()})")
        st.markdown(f"  [{item['url']}]({item['url']})")
