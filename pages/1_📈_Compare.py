import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide")
st.header("複数銘柄の株価パフォーマンス比較")

# st.selectboxをst.multiselectに変更
tickers = st.multiselect(
    "比較したい銘柄を選択してください",
    ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'],
    ['AAPL', 'MSFT', 'GOOGL'] # デフォルトで選択しておく銘柄
)

period = st.selectbox(
    "表示期間を選んでください",
    ('1mo', '3mo', '6mo', '1y', '2y', '5y', '10y'),
    index=3
)

# 銘柄が1つ以上選択されたら実行
if tickers:
    # yf.downloadは複数の銘柄を一度に取得できる
    data = yf.download(tickers, period=period)['Close']

    if not data.empty:
        # 正規化（全ての銘柄の初日の株価を100とする）
        normalized_data = data / data.iloc[0] * 100

        st.write(f"### 株価パフォーマンス比較チャート ({period})")
        st.line_chart(normalized_data)