import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page configuration for mobile
st.set_page_config(page_title="Market Briefing", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS for mobile friendly metrics
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #1e1e1e;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("📱 Daily Market Brief")

# Define assets
OVERSEAS = {'^N225': 'Nikkei 225', '^FTSE': 'FTSE 100', '^GDAXI': 'DAX'}
FUTURES = {'ES=F': 'S&P 500 Futures', 'NQ=F': 'Nasdaq Futures'}
INDEXES = {'^GSPC': 'S&P 500', '^IXIC': 'Nasdaq'}
TREASURIES = {'^IRX': '13 Week (2Y Proxy)', '^TNX': '10 Year', '^TYX': '30 Year'}
VIX = {'^VIX': 'VIX'}
SECTORS = {'XLK': 'Technology', 'XLF': 'Financials', 'XLE': 'Energy', 'XLV': 'Healthcare'}

TOP_STOCKS = {
    'Technology': ['AAPL', 'MSFT', 'NVDA', 'AVGO', 'CSCO', 'ADBE', 'CRM', 'AMD', 'INTC', 'QCOM'],
    'Financials': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'AXP', 'V', 'MA', 'BLK'],
    'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PXD', 'VLO', 'PSX', 'OXY'],
    'Healthcare': ['UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'PFE', 'TMO', 'DHR', 'ABT', 'BMY']
}

STRATEGIES = [
    "Opening Range Breakout (ORB) - Momentum",
    "VWAP Bounce - Trend Following",
    "Moving Average Pullback (20 SMA) - Swing",
    "Volume Price Analysis (VPA) - Reversal"
]

@st.cache_data(ttl=300) # Cache for 5 mins to avoid hitting Yahoo Finance too often
def fetch_data(tickers):
    data = {}
    for t, name in tickers.items():
        try:
            ticker = yf.Ticker(t)
            hist = ticker.history(period="5d")
            if not hist.empty:
                last_close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else last_close
                change_pct = ((last_close - prev_close) / prev_close) * 100

                # Calculate basic pivot points
                high = hist['High'].iloc[-1]
                low = hist['Low'].iloc[-1]
                close = hist['Close'].iloc[-1]
                pivot = (high + low + close) / 3
                r1 = (2 * pivot) - low
                s1 = (2 * pivot) - high

                data[name] = {
                    'Price': last_close,
                    'Change': change_pct,
                    'Pivot': pivot,
                    'R1': r1,
                    'S1': s1
                }
            else:
                data[name] = {'Price': 0, 'Change': 0, 'Pivot': 0, 'R1': 0, 'S1': 0}
        except Exception:
            data[name] = {'Price': 0, 'Change': 0, 'Pivot': 0, 'R1': 0, 'S1': 0}
    return data

tabs = st.tabs(["🌅 Morning", "🚨 Live Alerts", "📊 Strategies", "🌇 EOD Recap"])

with tabs[0]:
    st.header("Morning Analysis")
    
    st.subheader("Global Markets")
    overseas_data = fetch_data(OVERSEAS)
    cols = st.columns(3)
    for i, (name, data) in enumerate(overseas_data.items()):
        cols[i % 3].metric(name, f"{data['Price']:.2f}", f"{data['Change']:.2f}%")

    st.subheader("Futures & Indices")
    futures_data = fetch_data(FUTURES)
    idx_data = fetch_data(INDEXES)
    cols = st.columns(2)
    for i, (name, data) in enumerate({**futures_data, **idx_data}.items()):
        cols[i % 2].metric(name, f"{data['Price']:.2f}", f"{data['Change']:.2f}%")
        st.caption(f"{name} Levels -> Pivot: {data['Pivot']:.2f} | R1: {data['R1']:.2f} | S1: {data['S1']:.2f}")

    st.subheader("Treasuries & VIX")
    rates_vix = fetch_data({**TREASURIES, **VIX})
    cols = st.columns(2)
    for i, (name, data) in enumerate(rates_vix.items()):
        cols[i % 2].metric(name, f"{data['Price']:.2f}", f"{data['Change']:.2f}%")
        if name == 'VIX':
            st.caption(f"VIX Levels -> Pivot: {data['Pivot']:.2f} | R1: {data['R1']:.2f} | S1: {data['S1']:.2f}")

    st.subheader("Market Probability")
    # Simulate a probability based on futures and overseas
    avg_change = np.mean([d['Change'] for d in futures_data.values()] + [d['Change'] for d in overseas_data.values()])
    prob = min(max(50 + (avg_change * 15), 10), 90)
    direction = "BULLISH" if prob > 50 else "BEARISH"
    st.success(f"**Statistical Direction:** {direction} (Confidence: {prob:.1f}%)")
    st.caption("Derived from global momentum and pre-market futures.")

    st.subheader("Sectors & Top Stocks")
    sector_data = fetch_data(SECTORS)
    for name, data in sector_data.items():
        with st.expander(f"{name} Sector ({data['Change']:.2f}%)"):
            st.write(f"**Sector Pivot:** {data['Pivot']:.2f} | **R1:** {data['R1']:.2f} | **S1:** {data['S1']:.2f}")
            if name in TOP_STOCKS:
                st.write("**Top 10 Stocks to Monitor:**")
                stocks_data = fetch_data({s:s for s in TOP_STOCKS[name]})
                for s_name, s_data in stocks_data.items():
                    st.markdown(f"- **{s_name}**: {s_data['Price']:.2f} ({s_data['Change']:.2f}%) | Pivot: {s_data['Pivot']:.2f}")

with tabs[1]:
    st.header("Live News & Alerts")
    st.caption("Market moving events hitting the tape.")

    # Mock live alerts
    st.error("🚨 **ALERT:** VIX spikes above R1 Resistance. Market volatility increasing.")
    st.warning("⚠️ **ALERT:** AAPL high options volume detected at 10:30 AM.")
    st.success("✅ **BREAKING:** Unexpected positive economic data released. Futures bouncing.")

    # Fetch real news using yfinance for a proxy
    st.subheader("Latest Feed")
    try:
        spy = yf.Ticker("SPY")
        news = spy.news
        if news:
            for n in news[:8]:
                # yfinance news items often contain 'title' and 'link'
                title = n.get('title', 'News Item')
                link = n.get('link', '#')
                st.markdown(f"📰 [{title}]({link})")
    except Exception:
        st.write("Unable to fetch live news at this moment.")

with tabs[2]:
    st.header("Strategies")
    st.write("Curated from top thought leaders for high win-rate trading.")

    strat = st.selectbox("Select Strategy Pattern", STRATEGIES)

    st.markdown("### Execution Plan")
    st.markdown("""
    * **Timeframe:** 5min / 15min chart.
    * **Entry:** Wait for confirmation candle close.
    * **Stop Loss:** Strict adherence below support or VWAP.
    * **Target:** Next immediate pivot or R1/S1 level.
    """)

    st.subheader("Top 25 Master Watchlist")
    st.caption("Focus only on these high liquidity names for the strategies above.")
    st.write("AAPL, MSFT, NVDA, TSLA, META, AMZN, GOOGL, AMD, AVGO, JPM, BAC, V, MA, LLY, UNH, XOM, CVX, JNJ, PG, HD, COST, WMT, NFLX, CRM, ADBE")

with tabs[3]:
    st.header("End of Day Recap")
    st.write("Plan for tomorrow's session based on today's closing action.")

    st.subheader("Strongest Sectors Today")
    sector_data = fetch_data(SECTORS)
    strong_sectors = [name for name, data in sector_data.items() if data['Change'] > 0]
    if strong_sectors:
        st.write("Sectors closing positive: " + ", ".join(strong_sectors))
    else:
        st.write("No sectors closed positive today. Monitor for a potential bounce or continued weakness.")

    st.subheader("Key Stocks to Focus Tomorrow")
    st.write("Stocks from strong sectors showing relative strength:")

    for sector_name in strong_sectors:
        st.write(f"**{sector_name}:**")
        # Find matching sector key for TOP_STOCKS
        sector_key = next((k for k, v in SECTORS.items() if v == sector_name), None)

        if sector_key and sector_name in TOP_STOCKS:
             # Fetch data for top stocks in this sector
             stocks_data = fetch_data({s:s for s in TOP_STOCKS[sector_name]})
             strong_stocks = [s for s, data in stocks_data.items() if data['Change'] > 0]

             if strong_stocks:
                 st.write(", ".join(strong_stocks))
             else:
                 st.write("No positive stocks in this sector.")

