import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import requests
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

# === Portfolio Definition ===
portfolio_data = {
    "Ticker": ["FNV", "CFR.SW", "NOVO-B.CO", "NDA-FI.HE", "LLY", "AXON", "KD", "VWCE.DE", "VYM", "GRMNY"],
    "Company": [
        "Franco Nevada", "Richemont", "Novo Nordisk", "Nordea Bank",
        "Eli Lilly", "Axon Enterprise", "Kyndryl Holdings",
        "Vanguard FTSE All World", "Vanguard High Dividend", "Chimera Germany ETF"],
    "Shares": [120, 100, 7, 450, 12, 11, 30, 34, 31, 2500]
}
df = pd.DataFrame(portfolio_data)

FINNHUB_TOKEN = "d08j1rpr01qju5m6q6d0d08j1rpr01qju5m6q6dg"

@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        latest_price = hist["Close"].iloc[-1] if not hist.empty else None
        prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else latest_price
        change_pct = ((latest_price - prev_price) / prev_price) * 100 if prev_price else 0
        return latest_price, change_pct, hist
    except:
        return None, None, pd.DataFrame()

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
        return r.json()[:5]
    except:
        return []

# === Alerts Section ===
st.subheader("🔔 Alerts")
alerts = []
for i, row in df.iterrows():
    price, change, _ = get_stock_data(row["Ticker"])
    sentiment = get_finnhub_sentiment(row["Ticker"])
    if change is not None and change < -5:
        alerts.append(f"📉 {row['Ticker']}: Price dropped {change:.2f}%")
    if sentiment == "Negative":
        alerts.append(f"⚠️ {row['Ticker']}: Sentiment is Negative")

if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("No alerts today.")

# === Portfolio Snapshot ===
st.subheader("📋 Full Portfolio Table")
prices = []
changes = []
values = []
for ticker, shares in zip(df["Ticker"], df["Shares"]):
    price, change, _ = get_stock_data(ticker)
    prices.append(price)
    changes.append(change)
    values.append(price * shares if price else 0)

df["Price"] = prices
df["Daily % Change"] = changes
df["Total Value"] = values
portfolio_total = sum(v for v in values if v)
df["Weight %"] = [(v / portfolio_total) * 100 if portfolio_total else 0 for v in values]

st.dataframe(df[["Ticker", "Company", "Shares", "Price", "Daily % Change", "Total Value", "Weight %"]], use_container_width=True)

# === Portfolio Value Over Time ===
st.subheader("📈 Portfolio Value (6-Month Trend)")
history_df = pd.DataFrame()
for i, row in df.iterrows():
    ticker = row["Ticker"]
    shares = row["Shares"]
    _, _, hist = get_stock_data(ticker)
    if not hist.empty:
        hist = hist[["Close"]].rename(columns={"Close": ticker})
        hist[ticker] = hist[ticker] * shares
        if history_df.empty:
            history_df = hist
        else:
            history_df = history_df.join(hist, how='outer')

if not history_df.empty:
    history_df["Total"] = history_df.sum(axis=1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history_df.index, y=history_df["Total"], mode='lines', name='Total Value'))
    fig.update_layout(xaxis_title="Date", yaxis_title="Portfolio Value (USD)", height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough historical data to show chart.")

# === Interactive Ticker Explorer ===
st.subheader("🔍 Explore Individual Tickers")
ticker = st.selectbox("Select a stock:", df["Ticker"])
company = df[df["Ticker"] == ticker]["Company"].values[0]
st.markdown(f"### {company} ({ticker})")

try:
    hist = get_stock_data(ticker)[2]
    if hist.empty:
        st.warning("No price data available.")
    else:
        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2] if len(hist) > 1 else price
        change = ((price - prev) / prev) * 100 if prev != 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Price (USD)", f"{price:.2f}")
        col2.metric("Change (%)", f"{change:.2f}%", delta_color="inverse")
        col3.metric("Sentiment", get_finnhub_sentiment(ticker))

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode='lines', name='Close'))
        fig2.update_layout(title=f"{ticker} Price Chart (6mo)", xaxis_title="Date", yaxis_title="USD", height=400)
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load stock data: {e}")

st.markdown("### 📰 Latest News")
news_items = get_finnhub_news(ticker)
if not news_items:
    st.info("No recent news available.")
else:
    for item in news_items:
        st.markdown(f"- **{item['headline']}** ({item['source']}, {datetime.fromtimestamp(item['datetime']).date()})")
        st.markdown(f"  [{item['url']}]({item['url']})")


