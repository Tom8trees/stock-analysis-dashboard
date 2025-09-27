import streamlit as st
import yfinance as yf

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
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period)
    info = ticker.info

    st.header(f"{info['shortName']} ({ticker_symbol})")

    col1, col2 = st.columns(2)

    with col1:
        st.write("#### 株価チャート（終値）")
        st.line_chart(df['Close'])
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