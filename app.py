import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta

# === CONFIGURATION ===
FMP_API_KEY = "ugL4X7iZNw3wdkq7dFpnhZDujdEAkymy"
PORTFOLIO = [
    {"ticker": "FNV", "company": "Franco Nevada", "shares": 120},
    {"ticker": "CFR.SW", "company": "Richemont", "shares": 100},
    {"ticker": "NOVO-B.CO", "company": "Novo Nordisk", "shares": 7},
    {"ticker": "NDA-FI.HE", "company": "Nordea Bank", "shares": 450},
    {"ticker": "LLY", "company": "Eli Lilly", "shares": 12},
    {"ticker": "AXON", "company": "Axon Enterprise", "shares": 11},
    {"ticker": "KD", "company": "Kyndryl Holdings", "shares": 30},
    {"ticker": "VWCE.DE", "company": "Vanguard FTSE All World", "shares": 34},
    {"ticker": "VYM", "company": "Vanguard High Dividend", "shares": 31},
    {"ticker": "GRMNY", "company": "Chimera Germany ETF", "shares": 2500},
]

# === FETCH FUNCTIONS ===
def fetch_price_fmp(ticker):
    url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        return data[0]["price"], data[0].get("changesPercentage", 0)
    except:
        return None, None

def fetch_chart_fmp(ticker):
    end = datetime.now()
    start = end - timedelta(days=180)
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={start.date()}&to={end.date()}&apikey={FMP_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json().get("historical", [])
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        return df
    except:
        return None

def fetch_earnings_fmp(ticker):
    url = f"https://financialmodelingprep.com/api/v3/earning_calendar/{ticker}?apikey={FMP_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        return data[0].get("date", "N/A") if data else "N/A"
    except:
        return "N/A"

def fetch_dividend_fmp(ticker):
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{ticker}?apikey={FMP_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json().get("historical", [])
        return data[0].get("dividend", "N/A") if data else "N/A"
    except:
        return "N/A"

# === UI ===
st.set_page_config("JP's Portfolio Dashboard", layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

# === DATA AGGREGATION ===
df = pd.DataFrame(PORTFOLIO)
prices = []
changes = []
next_earnings = []
last_dividends = []
values = []

for row in df.itertuples():
    price, change = fetch_price_fmp(row.ticker)
    prices.append(price)
    changes.append(change)
    values.append(price * row.shares if price else 0)
    next_earnings.append(fetch_earnings_fmp(row.ticker))
    last_dividends.append(fetch_dividend_fmp(row.ticker))

df["Price"] = prices
df["Daily % Change"] = changes
df["Total Value"] = values
total_value = sum(v for v in values if v)
df["Weight %"] = [round(v / total_value * 100, 2) if total_value else 0 for v in values]
df["Next Earnings"] = next_earnings
df["Last Dividend"] = last_dividends

# === DISPLAY TABLE ===
st.subheader("📋 Full Portfolio Overview")
st.dataframe(df, use_container_width=True)

# === CHART ===
st.subheader("📈 Portfolio Value Summary (Rolling)")
chart_data = pd.DataFrame()
for row in df.itertuples():
    hist = fetch_chart_fmp(row.ticker)
    if hist is not None:
        hist["value"] = hist["close"] * row.shares
        if chart_data.empty:
            chart_data = hist[["date", "value"]].copy()
            chart_data.rename(columns={"value": row.ticker}, inplace=True)
        else:
            chart_data = chart_data.merge(hist[["date", "value"]], on="date", how="outer")
            chart_data.rename(columns={"value": row.ticker}, inplace=True)

if not chart_data.empty:
    chart_data = chart_data.sort_values("date")
    chart_data.set_index("date", inplace=True)
    chart_data["Total"] = chart_data.sum(axis=1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data["Total"], name="Total Portfolio"))
    fig.update_layout(height=500, margin=dict(l=30, r=30, t=30, b=30))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Portfolio value chart not available due to rate limit or missing data.")
