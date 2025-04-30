# JP Portfolio Dashboard App with FMP + YahooQuery Fallback

import streamlit as st
import pandas as pd
import yfinance as yf
from yahooquery import Ticker as YQ_Ticker
import requests

# --- CONFIG ---
FMP_API_KEY = "ugL4X7iZNw3wdkq7dFpnhZDujdEAkymy"

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
        response = requests.get(url)
        data = response.json()
        if isinstance(data, list) and data:
            return {
                "price": data[0].get("price"),
                "changePercent": data[0].get("changesPercentage"),
                "source": "FMP"
            }
    except Exception:
        return None


def get_yq_data(ticker):
    try:
        yq = YQ_Ticker(ticker)
        price_data = yq.price.get(ticker)
        if isinstance(price_data, dict):
            reg_price = price_data.get("regularMarketPrice")
            pct_change = price_data.get("regularMarketChangePercent")
            return {
                "price": reg_price,
                "changePercent": pct_change,
                "source": "YahooQuery"
            }
    except Exception:
        return None

# --- LOAD & ENRICH DATA ---
data = []

total_portfolio_value = 0

for entry in portfolio:
    ticker = entry["ticker"]
    shares = entry["shares"]

    result = get_fmp_data(ticker)
    if not result:
        result = get_yq_data(ticker)

    if result and result["price"]:
        price = result["price"]
        total_value = price * shares
        total_portfolio_value += total_value
        data.append({
            "ticker": ticker,
            "company": entry["company"],
            "shares": shares,
            "Price": round(price, 2),
            "Daily % Change": round(result["changePercent"], 4) if result["changePercent"] is not None else "N/A",
            "Total Value": round(total_value, 2),
            "Source": result["source"]
        })
    else:
        data.append({
            "ticker": ticker,
            "company": entry["company"],
            "shares": shares,
            "Price": None,
            "Daily % Change": None,
            "Total Value": 0,
            "Source": "None"
        })

# Add weight %
for row in data:
    row["Weight %"] = round((row["Total Value"] / total_portfolio_value) * 100, 2) if total_portfolio_value else 0

# --- STREAMLIT UI ---
st.set_page_config(layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

st.dataframe(pd.DataFrame(data))

