import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.subheader('株価分析ダッシュボード')

with st.expander("銘柄や期間を変更する 🔽"):
    ticker_symbol = st.selectbox('銘柄を選んでください', ('AAPL', 'MSFT', 'GOOGL', 'TSLA'))
    period = st.selectbox('表示期間を選んでください', ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y'), index=5)

try:
    # --- データ取得・計算ロジック ---
    period_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825, '10y': 3650}
    days_to_subtract = period_map.get(period)
    end_date = datetime.now().date()
    view_start_date = end_date - timedelta(days=days_to_subtract)
    fetch_start_date = view_start_date - timedelta(days=70)

    ticker = yf.Ticker(ticker_symbol)
    df_extended = ticker.history(start=fetch_start_date, end=end_date)
    
    df_extended['EMA20'] = ta.ema(df_extended['Close'], length=20)
    df_extended['EMA50'] = ta.ema(df_extended['Close'], length=50)
    df_extended['RSI'] = ta.rsi(df_extended['Close'], length=14)
    df_extended.ta.macd(close='Close', fast=12, slow=26, signal=9, append=True)
    
    df_extended.dropna(inplace=True)
    
    view_start_date_aware = pd.to_datetime(view_start_date).tz_localize('America/New_York')
    df_extended.index = df_extended.index.tz_localize(None)
    df = df_extended[df_extended.index >= pd.to_datetime(view_start_date)]

    info = ticker.info
    st.subheader(f"{info.get('shortName', ticker_symbol)} ({ticker_symbol})")
    
    # --- あなたが設計した最終レイアウト ---
    
    col1, col2 = st.columns([2, 1])

    # --- 左カラム ---
    with col1:
        st.subheader('株価チャート')
        fig_price = go.Figure()
        fig_price.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='ローソク足'))
        long_period_threshold = ('3mo', '6mo', '1y', '2y', '5y', '10y')
        if period in long_period_threshold:
            fig_price.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='orange')))
            fig_price.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name='EMA 50', line=dict(color='purple')))
        fig_price.update_layout(xaxis_rangeslider_visible=False, yaxis_title='株価 (USD)', margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_price, use_container_width=True)

        # サブカラム
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.subheader("RSI")
            st.line_chart(df['RSI'])
        with sub_col2:
            st.subheader("MACD")
            fig_macd = go.Figure()
            # MACDヒストグラムの列名を修正（MACDh_...）
            fig_macd.add_trace(go.Bar(x=df.index, y=df['MACDh_12_26_9'], name='ヒストグラム'))
            fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], name='MACD', line=dict(color='blue')))
            fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], name='シグナル', line=dict(color='orange')))
            fig_macd.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_macd, use_container_width=True)

    # --- 右カラム ---
    with col2:
        st.subheader("最新の株価指標")
        if len(df['Close']) > 1:
            latest_close = df['Close'].iloc[-1]
            previous_close = df['Close'].iloc[-2]
            change = latest_close - previous_close
            change_percent = (change / previous_close) * 100
            st.metric(label="最新終値", value=f"${latest_close:,.2f}", delta=f"{change:,.2f} ({change_percent:.2f}%)")
        else:
            st.metric(label="最新終値", value=f"${df['Close'].iloc[-1]:,.2f}", delta="N/A")
        
        st.subheader("出来高")
        st.bar_chart(df['Volume'])
        
        st.subheader("株価データ")
        st.dataframe(df.tail()) # 全件表示だと長すぎるので.tail()に戻しました
        
        st.subheader("企業情報")
        with st.expander("詳細を見る"):
            st.json(info)
            
except Exception as e:
    st.error(f"データを取得できませんでした。エラー: {e}")