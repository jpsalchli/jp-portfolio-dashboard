import streamlit as st
import pandas as pd
from yahooquery import Ticker
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

# === Streamlit Setup ===
st.set_page_config(page_title="JP Portfolio Dashboard", layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

# === Load Data ===
tickers = [entry["ticker"] for entry in portfolio]
t = Ticker(tickers)
quote = t.quote_type
price_data = t.price

results = []
total_value = 0

for entry in portfolio:
    ticker = entry["ticker"]
    shares = entry["shares"]
    company = entry["company"]

    info = price_data.get(ticker)
    if isinstance(info, dict) and info.get("regularMarketPrice"):
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

# Calculate weights
for row in results:
    row["Weight %"] = round((row["Total Value"] / total_value * 100), 2) if total_value else 0

# === Display Table ===
df = pd.DataFrame(results)
st.subheader("📋 Portfolio Snapshot")
st.dataframe(df, use_container_width=True)

# === Footer ===
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")





