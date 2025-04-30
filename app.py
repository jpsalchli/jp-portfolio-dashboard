import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# === Portfolio Definition ===
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

# === Fetch Raw Quote Data ===
def fetch_quotes(tickers):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={','.join(tickers)}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()["quoteResponse"]["result"]
        return {item["symbol"]: item for item in data}
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}

# === Streamlit Setup ===
st.set_page_config(page_title="JP Portfolio Dashboard", layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard (Raw Yahoo API Mode)")

# === Load Data ===
ticker_list = [item["ticker"] for item in portfolio]
quote_data = fetch_quotes(ticker_list)

results = []
total_value = 0

for entry in portfolio:
    ticker = entry["ticker"]
    company = entry["company"]
    shares = entry["shares"]
    info = quote_data.get(ticker)

    if info and info.get("regularMarketPrice"):
        price = info["regularMarketPrice"]
        change = info.get("regularMarketChangePercent")
        value = round(price * shares, 2)
        results.append({
            "Ticker": ticker,
            "Company": company,
            "Shares": shares,
            "Price": round(price, 2),
            "Daily % Change": round(change, 2) if change else "N/A",
            "Total Value": value
        })
        total_value += value
    else:
        results.append({
            "Ticker": ticker,
            "Company": company,
            "Shares": shares,
            "Price": "N/A",
            "Daily % Change": "N/A",
            "Total Value": 0
        })

# Add weight
for row in results:
    row["Weight %"] = round((row["Total Value"] / total_value * 100), 2) if total_value else 0

# === Display ===
df = pd.DataFrame(results)
st.dataframe(df, use_container_width=True)

st.caption(f"Data pulled via direct Yahoo Finance quote API. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")





