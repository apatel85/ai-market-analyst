import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Market Agent", layout="wide")
st.title("🤖 AI Financial Analyst Agent")

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("Control Panel")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 30, 300, 60)

# --- FUNCTION: FETCH DATA ---
def get_market_snapshot():
    # 1. Global Context (Indices)
    global_tickers = {'^N225': 'Nikkei 225', '^FTSE': 'FTSE 100', '^GDAXI': 'DAX'}
    global_data = []
    for ticker, name in global_tickers.items():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) > 1:
            change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            global_data.append({"Index": name, "Change %": round(change, 2)})
    
    # 2. Sector Performance (US)
    sectors = {'XLE': 'Energy', 'XLK': 'Tech', 'XLF': 'Finance', 'XLV': 'Healthcare'}
    sector_data = []
    for ticker, name in sectors.items():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if len(hist) > 0:
            change = ((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100
            sector_data.append({"Sector": name, "Change %": round(change, 2)})
            
    return pd.DataFrame(global_data), pd.DataFrame(sector_data)

# --- FUNCTION: MOCK AI PREDICTION (Replace with actual LLM call) ---
def generate_ai_prediction(context_df):
    # In real use, you would send 'context_df' to GPT-4 here
    return """
    **AI Market Outlook:**
    * **Sentiment:** Bearish Divergence. 
    * **Strategy:** Rotate out of Tech (XLK), into Energy (XLE).
    * **Top Pick:** Exxon Mobil (XOM) - Breakout above $115 imminent.
    """

# --- TABS LAYOUT ---
tab1, tab2, tab3 = st.tabs(["📈 Pre-Market", "🚨 Live Monitor", "📝 Post-Market"])

with tab1:
    st.header(f"Pre-Market Analysis ({datetime.now().strftime('%Y-%m-%d')})")
    
    if st.button("Run Analysis"):
        with st.spinner('Analyzing Global Markets & News...'):
            global_df, sector_df = get_market_snapshot()
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Global Context")
                st.dataframe(global_df, hide_index=True)
            with col2:
                st.subheader("Sector Momentum")
                fig = px.bar(sector_df, x='Sector', y='Change %', color='Change %', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, use_container_width=True)
            
            st.success("Analysis Complete")
            st.markdown("### 🧠 AI Strategic Output")
            st.markdown(generate_ai_prediction(sector_df))

with tab2:
    st.header("Live News & Alerts")
    st.info("Monitoring continuous news feed...")
    # This is where you would loop your NewsAPI check
    st.write("10:02 AM: Unusual Volume detected in NVDA (PUT options).")
    st.write("09:45 AM: Fed Chair speech scheduled for 2 PM.")

with tab3:
    st.header("Post-Market Recap")
    st.write("Available after 4:30 PM EST.")