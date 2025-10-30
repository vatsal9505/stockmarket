import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Market Dashboard", layout="wide", page_icon="📈")

st.title("📈 Stock Market Analysis Dashboard")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1e1e1e, #4f4f4f);
    color: white;
}
</style>
""", unsafe_allow_html=True)


st.sidebar.header("Select Data Source")
data_source = st.sidebar.radio("Choose Data Source:", ["📊 Upload CSV", "🌐 Alpha Vantage API"])

if data_source == "🌐 Alpha Vantage API":
    symbol = st.text_input("Enter Stock Symbol (e.g. AAPL, MSFT, TSLA):", "AAPL")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    api_key = "9CBBY4HDHPHL33NG"

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": api_key
    }

    r = requests.get(url, params=params)
    response = r.json()

    if "Time Series (Daily)" not in response:
        st.error("❌ Failed to fetch data. Please check your API key or stock symbol.")
        st.stop()

    data = response["Time Series (Daily)"]
    df = pd.DataFrame(data).T
    df.index = pd.to_datetime(df.index)
    df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    }, inplace=True)
    df = df.astype(float)

else:

    st.sidebar.write("Upload your stock CSV file (e.g., from Yahoo Finance)")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, skiprows=1)
    else:
        df = pd.read_csv("Data.csv", skiprows=1)

    df.rename(columns={df.columns[0]: "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    stock = st.selectbox("Select Stock", df.columns[1:])
    df = df[[stock]]
    df.rename(columns={stock: "Close"}, inplace=True)
    start_date = df.index.min()
    end_date = df.index.max()


df_filtered = df[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))]

if df_filtered.empty:
    st.warning("⚠️ No data in the selected date range.")
    st.stop()

st.write("Available Data:", df.index.min(), "→", df.index.max())
st.write("You selected:", start_date, "→", end_date)

st.subheader(f"📊 Closing Price Trend")
fig = px.line(df_filtered, x=df_filtered.index, y="Close", title="Closing Price Over Time")
st.plotly_chart(fig, use_container_width=True)

if "Volume" in df_filtered.columns:
    st.subheader("📊 Daily Trading Volume")
    fig_vol = px.bar(df_filtered, x=df_filtered.index, y="Volume", title="Daily Trading Volume")
    st.plotly_chart(fig_vol, use_container_width=True)

df_filtered["MA20"] = df_filtered["Close"].rolling(20).mean()
df_filtered["MA50"] = df_filtered["Close"].rolling(50).mean()

st.subheader("📈 Moving Averages (20-day & 50-day)")
fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["Close"], mode='lines', name='Close'))
fig_ma.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["MA20"], mode='lines', name='MA20'))
fig_ma.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["MA50"], mode='lines', name='MA50'))
fig_ma.update_layout(title="Moving Averages Over Time")
st.plotly_chart(fig_ma, use_container_width=True)

if all(col in df_filtered.columns for col in ["Open", "High", "Low", "Close"]):
    st.subheader("🕯️ Candlestick Chart")
    fig_candle = go.Figure(data=[go.Candlestick(
        x=df_filtered.index,
        open=df_filtered["Open"],
        high=df_filtered["High"],
        low=df_filtered["Low"],
        close=df_filtered["Close"]
    )])
    fig_candle.update_layout(title="Candlestick Chart", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_candle, use_container_width=True)

df_filtered["Daily Change %"] = df_filtered["Close"].pct_change() * 100
st.subheader("💹 Daily Percentage Change")
fig_pct = px.line(df_filtered, x=df_filtered.index, y="Daily Change %", title="Daily % Change in Price")
st.plotly_chart(fig_pct, use_container_width=True)

df_filtered["Cumulative Return"] = (1 + df_filtered["Close"].pct_change()).cumprod()
st.subheader("📈 Cumulative Return")
fig_cum = px.line(df_filtered, x=df_filtered.index, y="Cumulative Return", title="Cumulative Return Over Time")
st.plotly_chart(fig_cum, use_container_width=True)

st.write("### 📋 Raw Data")
st.dataframe(df_filtered)
