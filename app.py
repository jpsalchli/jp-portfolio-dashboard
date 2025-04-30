import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta
import time

# --- Portfolio Data ---
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

portfolio_df = pd.DataFrame(portfolio)
portfolio_df.set_index("ticker", inplace=True)

# --- Fetch Market Data ---
def fetch_data_yf(tickers):
    try:
        tickers_str = " ".join(tickers)
        data = yf.Tickers(tickers_str)
        prices, changes = {}, {}
        for ticker in tickers:
            try:
                info = data.tickers[ticker].info
                price = info.get("regularMarketPrice")
                change = info.get("regularMarketChangePercent")
                prices[ticker] = price
                changes[ticker] = change
            except Exception:
                prices[ticker] = None
                changes[ticker] = None
        return prices, changes
    except Exception:
        return {}, {}

# --- Streamlit App Layout ---
st.set_page_config(page_title="JP's Portfolio Dashboard", layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

with st.spinner("Fetching latest prices..."):
    tickers = portfolio_df.index.tolist()
    prices, changes = fetch_data_yf(tickers)

    total_values = []
    weightings = []
    total_portfolio_value = 0

    for ticker in tickers:
        price = prices.get(ticker)
        shares = portfolio_df.loc[ticker, "shares"]
        value = price * shares if price is not None else 0
        total_values.append(value)
        total_portfolio_value += value

    for value in total_values:
        weight = round(value / total_portfolio_value * 100, 2) if total_portfolio_value else 0
        weightings.append(weight)

    portfolio_df["Price"] = portfolio_df.index.map(prices.get)
    portfolio_df["Daily % Change"] = portfolio_df.index.map(changes.get)
    portfolio_df["Total Value"] = total_values
    portfolio_df["Weight %"] = weightings

# --- Portfolio Table ---
st.subheader("📋 Full Portfolio Snapshot")
st.dataframe(portfolio_df.reset_index(), use_container_width=True)

# --- Summary Chart ---
st.subheader("📈 Portfolio Allocation by Weight")
fig = go.Figure(data=[
    go.Pie(
        labels=portfolio_df["company"],
        values=portfolio_df["Weight %"],
        hole=0.4,
        textinfo="label+percent",
    )
])
fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
st.plotly_chart(fig, use_container_width=True)

# --- Last Updated ---
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")





