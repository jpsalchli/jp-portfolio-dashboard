import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta
from finnhub import Client as FinnhubClient
from yahooquery import Ticker as YQ_Ticker
import time

# === CONFIGURATION ===
FINNHUB_KEY = "d08j1rpr01qju5m6q6d0d08j1rpr01qju5m6q6dg"
FMP_KEY = "ugL4X7iZNw3wdkq7dFpnhZDujdEAkymy"
finnhub = FinnhubClient(api_key=FINNHUB_KEY)

portfolio = [
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

@st.cache_data(ttl=3600)
def fetch_from_fmp(ticker):
    try:
        url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_KEY}"
        r = requests.get(url)
        data = r.json()
        if data:
            d = data[0]
            return d["price"], d.get("changesPercentage")
    except:
        return None, None

@st.cache_data(ttl=3600)
def fetch_from_yq(ticker):
    try:
        t = YQ_Ticker(ticker)
        p = t.price[ticker]
        return p["regularMarketPrice"], p.get("regularMarketChangePercent")
    except:
        return None, None

def get_price_and_change(ticker):
    price, change = fetch_from_fmp(ticker)
    if price is None:
        price, change = fetch_from_yq(ticker)
    return price, change

# === APP ===
st.set_page_config(page_title="JP Portfolio Dashboard", layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

rows = []
total_value = 0

for entry in portfolio:
    t = entry["ticker"]
    name = entry["company"]
    shares = entry["shares"]

    price, change = get_price_and_change(t)
    value = round(price * shares, 2) if price else 0
    total_value += value

    rows.append({
        "ticker": t,
        "company": name,
        "shares": shares,
        "Price": price,
        "Daily % Change": change,
        "Total Value": value,
        "Source": "FMP" if price else "YQ"
    })

df = pd.DataFrame(rows)
df["Weight %"] = (df["Total Value"] / total_value * 100).round(2)

st.dataframe(df, use_container_width=True)

st.caption("Prices fetched from FMP, fallback to YahooQuery where necessary. Cached for 1 hour.")




