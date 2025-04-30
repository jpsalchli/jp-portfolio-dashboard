import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import requests
import yfinance as yf
from datetime import datetime, timedelta

# ---------------- CONFIG ------------------
st.set_page_config(page_title="JP Portfolio Dashboard", layout="wide")
st.title("📊 JP's Investment Portfolio Dashboard")

# ---------------- DATA ------------------
PORTFOLIO = [
    {"Ticker": "FNV", "Company": "Franco Nevada", "Shares": 120},
    {"Ticker": "CFR.SW", "Company": "Richemont", "Shares": 100},
    {"Ticker": "NOVO-B.CO", "Company": "Novo Nordisk", "Shares": 7},
    {"Ticker": "NDA-FI.HE", "Company": "Nordea Bank", "Shares": 450},
    {"Ticker": "LLY", "Company": "Eli Lilly", "Shares": 12},
    {"Ticker": "AXON", "Company": "Axon Enterprise", "Shares": 11},
    {"Ticker": "KD", "Company": "Kyndryl Holdings", "Shares": 30},
    {"Ticker": "VWCE.DE", "Company": "Vanguard FTSE All World", "Shares": 34},
    {"Ticker": "VYM", "Company": "Vanguard High Dividend", "Shares": 31},
    {"Ticker": "GRMNY", "Company": "Chimera Germany ETF", "Shares": 2500},
]

FMP_API_KEY = "ugL4X7iZNw3wdkq7dFpnhZDujdEAkymy"

# ---------------- HELPERS ------------------
def fetch_price_data(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="6mo")
        return hist["Close"]
    except:
        return None

def get_price(ticker):
    try:
        return yf.Ticker(ticker).info.get("regularMarketPrice", None)
    except:
        return None

def get_daily_change(ticker):
    try:
        data = yf.Ticker(ticker).history(period="2d")
        if len(data) == 2:
            return ((data["Close"][-1] - data["Close"][-2]) / data["Close"][-2]) * 100
    except:
        return None

def get_fmp_data(ticker, key):
    url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={key}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        result = r.json()
        if result:
            return {
                "Next Earnings": result[0].get("earningsAnnouncement", "N/A"),
                "Last Dividend": result[0].get("lastDiv", "N/A")
            }
    except:
        return {"Next Earnings": "N/A", "Last Dividend": "N/A"}

# ---------------- MAIN DISPLAY ------------------
tickers = [x["Ticker"] for x in PORTFOLIO]
stocks_df = pd.DataFrame(PORTFOLIO)
stocks_df["Price"] = stocks_df["Ticker"].apply(get_price)
stocks_df["Daily % Change"] = stocks_df["Ticker"].apply(get_daily_change)
stocks_df["Total Value"] = stocks_df["Price"] * stocks_df["Shares"]
total_portfolio_value = stocks_df["Total Value"].sum()
stocks_df["Weight %"] = stocks_df["Total Value"] / total_portfolio_value * 100

# FMP API fallback earnings & dividends
earnings = []
dividends = []
for ticker in stocks_df["Ticker"]:
    result = get_fmp_data(ticker, FMP_API_KEY)
    earnings.append(result["Next Earnings"])
    dividends.append(result["Last Dividend"])

stocks_df["Next Earnings"] = earnings
stocks_df["Last Dividend"] = dividends

# ----------------- PLOT ------------------
try:
    hist_total = []
    for _, row in stocks_df.iterrows():
        series = fetch_price_data(row["Ticker"])
        if series is not None:
            hist_total.append(series * row["Shares"])

    if hist_total:
        combined = pd.concat(hist_total, axis=1).fillna(0)
        combined["Total"] = combined.sum(axis=1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=combined.index, y=combined["Total"], name="Portfolio Value"))
        fig.update_layout(title="Portfolio Total Value Over 6 Months", yaxis_title="Value", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("Unable to plot chart now. Data may be rate-limited.")

# ----------------- DISPLAY TABLE ------------------
st.subheader("Full Portfolio Snapshot")
st.dataframe(stocks_df[["Ticker", "Company", "Shares", "Price", "Daily % Change", "Total Value", "Weight %", "Next Earnings", "Last Dividend"]])

# ----------------- ALERTS ------------------
st.subheader("Alerts")
alerts = []
for _, row in stocks_df.iterrows():
    if row["Daily % Change"] and abs(row["Daily % Change"]) > 4:
        alerts.append(f"{row['Ticker']} moved {row['Daily % Change']:.2f}% today.")
if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("No alerts triggered today.")




