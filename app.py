# JP Portfolio Dashboard App with FMP + YahooQuery + Timeout/Error Handling

import streamlit as st
import pandas as pd
import requests
from yahooquery import Ticker as YQ_Ticker

# --- CONFIG ---
FMP_API_KEY = "ugL4X7iZNw3wdkq7dFpnhZDujdEAkymy"
REQUEST_TIMEOUT = 5  # seconds

# --- PORTFOLIO SETUP ---
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

# --- HELPERS ---
def get_fmp_data(ticker):
    url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        data = response.json()
        if isinstance(data, list) and data:
            return {
                "price": data[0].get("price"),
                "changePercent": data[0].get("changesPercentage"),
                "source": "FMP"
            }
    except Exception as e:
        print(f"FMP error for {ticker}: {e}")
    return None

def get_yq_data(ticker):
    try:
        yq = YQ_Ticker(ticker)
        price_data = yq.price.get(ticker)
        if isinstance(price_data, dict) and "regularMarketPrice" in price_data:
            return {
                "price": price_data.get("regularMarketPrice"),
                "changePercent": price_data.get("regularMarketChangePercent"),
                "source": "YahooQuery"
            }
    except Exception as e:
        print(f"YahooQuery error for {ticker}: {e}")
    return None

# --- LOAD DATA ---
st.set_page_config(layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

results = []
total_value = 0

with st.spinner("Fetching portfolio data..."):
    for entry in portfolio:
        ticker = entry["ticker"]
        shares = entry["shares"]

        data = get_fmp_data(ticker)
        if not data:
            data = get_yq_data(ticker)

        if data and data["price"]:
            price = data["price"]
            change = data.get("changePercent", 0)
            value = price * shares
            results.append({
                "Ticker": ticker,
                "Company": entry["company"],
                "Shares": shares,
                "Price": round(price, 2),
                "Daily % Change": round(change, 2) if change else "N/A",
                "Total Value": round(value, 2),
                "Source": data["source"]
            })
            total_value += value
        else:
            results.append({
                "Ticker": ticker,
                "Company": entry["company"],
                "Shares": shares,
                "Price": "N/A",
                "Daily % Change": "N/A",
                "Total Value": 0,
                "Source": "Unavailable"
            })

# --- FINALIZE TABLE ---
for row in results:
    row["Weight %"] = round((row["Total Value"] / total_value) * 100, 2) if total_value else 0

# --- DISPLAY ---
df = pd.DataFrame(results)
if df.empty:
    st.error("No data could be loaded. Please try again later.")
else:
    st.dataframe(df, use_container_width=True)


