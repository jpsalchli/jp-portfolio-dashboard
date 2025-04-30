
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="JP Portfolio Dashboard", layout="wide")

st.title("📊 JP's Investment Portfolio Dashboard")

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

df = pd.DataFrame(portfolio)

if st.button("🔄 Refresh Prices"):
    df["Price"] = [round(random.uniform(10, 900), 2) for _ in df.index]
    df["Daily % Change"] = [round(random.uniform(-3, 3), 2) for _ in df.index]
    df["Total Value"] = df["Price"] * df["shares"]
    total_portfolio_value = df["Total Value"].sum()
    df["Weight %"] = round(df["Total Value"] / total_portfolio_value * 100, 2)
    df["Source"] = "Placeholder"
else:
    df["Price"] = df["Daily % Change"] = df["Total Value"] = df["Weight %"] = 0
    df["Source"] = None

st.dataframe(df, use_container_width=True)
