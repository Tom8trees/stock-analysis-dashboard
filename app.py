import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Price Viewer", layout="wide")
st.title("Stock Price Viewer")

st.sidebar.header('銘柄と期間を選択')

ticker_symbol = st.sidebar.selectbox(
    '銘柄を選択してください',
    ('AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA')
)
period = st.sidebar.selectbox(
    '期間を選択してください',
    ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y')
)


try:
    period_map = {
        '1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, 
        '1y': 365, '2y': 730, '5y': 1825, '10y': 3650
    }
    days_to_subtract = period_map.get(period)

    end_date = datetime.now().date()
    view_start_date = end_date - timedelta(days=days_to_subtract)
    fetch_start_date = view_start_date - timedelta(days=70)

    ticker = yf.Ticker(ticker_symbol)
    df_extended = ticker.history(start=fetch_start_date, end=end_date)
    df_extended['EMA20'] = ta.ema(df_extended['Close'], length=20)
    df_extended['EMA50'] = ta.ema(df_extended['Close'], length=50)
    # df_extended['SMA20'] = df_extended['Close'].rolling(window=20).mean()
    # df_extended['SMA50'] = df_extended['Close'].rolling(window=50).mean()
    df_extended['RSI'] = ta.rsi(df_extended['Close'], length=14)
    df_extended.ta.macd(close='Close', fast=12, slow=26, signal=9, append=True)

    view_start_date_aware = pd.to_datetime(view_start_date).tz_localize('America/New_York')
    df = df_extended[df_extended.index >= view_start_date_aware]

    info = ticker.info

    st.header(f"{info['shortName']} ({ticker_symbol})")

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='ローソク足'
            )
        )

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['EMA20'],
            mode='lines',
            line=dict(color='blue', width=1),
            name='EMA20'
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['EMA50'],
            mode='lines',
            line=dict(color='red', width=1),
            name='EMA50'
        ))

        fig.update_layout(xaxis_rangeslider_visible=False, yaxis_title='価格 (USD)', title='株価チャート（終値）')

        st.plotly_chart(fig)

        st.write("#### RSI")
        df['RSI'] = ta.rsi(df['Close'], length=14)
        st.line_chart(df['RSI'])

        st.header("MACD")
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Bar(
            x=df.index,
            y=df['MACD_12_26_9'],
            name='ヒストグラム')
        )
        fig_macd.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD_12_26_9'],
            mode='lines',
            line=dict(color='blue', width=1),
            name='MACD'
        ))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], line=dict(color='orange', width=1), name='シグナル'))
        st.plotly_chart(fig_macd, use_container_width=True)

        with st.expander('MACDの見方📕'):
            st.write("""
                **MACD (マックディー)** は、トレンドの方向性と勢いを測る指標です。
                - **ゴールデンクロス**: MACDライン（青）がシグナルライン（オレンジ）を下から上に抜けたら、**買い**のサインとされます。📈
                - **デッドクロス**: MACDßラインがシグナルラインを上から下に抜けたら、**売り**のサインとされます。📉
                - **ヒストグラム**: 2本の線の乖離を示し、0ラインの上にあれば上昇トレンド、下にあれば下降トレンドの勢いを示します。
            """)

        st.write("#### 株価チャート（出来高）")
        st.bar_chart(df['Volume'])
        st.dataframe(df)

    with col2:
        st.header("最新の株価指標")
        latest_close = df['Close'].iloc[-1]
        previous_close = df['Close'].iloc[-2]
        change = latest_close - previous_close
        change_percent = (change / previous_close) * 100
        
        st.metric(label='最新終値', value=f"${latest_close:,.2f}", delta=f"{change:,.2f} ({change_percent:.2f}%)")

        st.header("株価データ")
        st.dataframe(df.tail())

        with st.expander('企業情報の詳細を見る'):
            st.json(info)        

except Exception as e:
    st.error(f"データの取得中にエラーが発生しました: {e}")