import streamlit as st
import pandas as pd
import random

# -------------------------------
# Portfolio Configuration
# -------------------------------
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

# -------------------------------
# Simulated Price Generation
# -------------------------------
def generate_prices():
    return [
        {
            **stock,
            "Price": round(random.uniform(10, 1000), 2),
            "Daily % Change": round(random.uniform(-2, 2), 4),
        }
        for stock in portfolio
    ]

# -------------------------------
# Main App
# -------------------------------
st.set_page_config(page_title="JP's Investment Portfolio", layout="wide")

st.title("📊 JP's Investment Portfolio Dashboard")
st.caption("Fast-loading version with simulated prices for testing")

if st.button("🔁 Refresh Prices"):
    st.session_state["data"] = generate_prices()

if "data" not in st.session_state:
    st.session_state["data"] = generate_prices()

df = pd.DataFrame(st.session_state["data"])
df["Total Value"] = df["shares"] * df["Price"]
df["Weight %"] = round(df["Total Value"] / df["Total Value"].sum() * 100, 2)

st.dataframe(df, use_container_width=True)

