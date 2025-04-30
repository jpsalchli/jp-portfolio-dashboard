# JP Portfolio Dashboard – Optimized with Caching and Batched FMP API

import streamlit as st
import pandas as pd
import requests
from yahooquery import Ticker as YQ_Ticker

# --- CONFIG ---
FMP_API_KEY = "ugL4X7iZNw3wdkq7dFpnhZDujdEAkymy"
FMP_QUOTE_URL = "https://financialmodelingprep.com/api/v3/quote/"

# --- PORTFOLIO ---
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

@st.cache_data(ttl=900)
def fetch_fmp_batch(tickers):
    symbols = ",".join(tickers)
    url = f"{FMP_QUOTE_URL}{symbols}?apikey={FMP_API_KEY}"
    try:
        r = requests.get(url, timeout=6)
        return {d["symbol"]: d for d in r.json() if "price" in d}
    except Exception as e:
        print(f"FMP batch error: {e}")
        return {}

@st.cache_data(ttl=900)
def fetch_yq_fallback(ticker):
    try:
        yq = YQ_Ticker(ticker)
        p = yq.price.get(ticker)
        if isinstance(p, dict):
            return {
                "price": p.get("regularMarketPrice"),
                "change": p.get("regularMarketChangePercent"),
                "source": "YahooQuery"
            }
    except Exception as e:
        print(f"YahooQuery error for {ticker}: {e}")
    return None

# --- LOAD & PROCESS ---
st.set_page_config(layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

results = []
total_value = 0

ticker_list = [entry["ticker"] for entry in portfolio]
fmp_data = fetch_fmp_batch(ticker_list)

for entry in portfolio:
    ticker = entry["ticker"]
    shares = entry["shares"]
    company = entry["company"]

    info = fmp_data.get(ticker)
    source = "FMP"

    if not info:
        fallback = fetch_yq_fallback(ticker)
        if fallback:
            info = fallback
            source = fallback["source"]

    if info and info.get("price"):
        price = info["price"]
        change = info.get("change") or info.get("changesPercentage")
        value = price * shares
        results.append({
            "Ticker": ticker,
            "Company": company,
            "Shares": shares,
            "Price": round(price, 2),
            "Daily % Change": round(change, 2) if change else "N/A",
            "Total Value": round(value, 2),
            "Source": source
        })
        total_value += value
    else:
        results.append({
            "Ticker": ticker,
            "Company": company,
            "Shares": shares,
            "Price": "N/A",
            "Daily % Change": "N/A",
            "Total Value": 0,
            "Source": "Unavailable"
        })

for row in results:
    row["Weight %"] = round((row["Total Value"] / total_value) * 100, 2) if total_value else 0

# --- DISPLAY ---
df = pd.DataFrame(results)
if df.empty:
    st.error("No data could be retrieved. Try again later.")
else:
    st.dataframe(df, use_container_width=True)


