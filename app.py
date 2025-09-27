import streamlit as st
import pandas as pd
import os
import concurrent.futures
import random
from datetime import datetime
import warnings

from script.tickers import get_ticker_nse
from script.trade_calculator import request_to_api_loacal_host
from script.trade_performance import trade_performance_calculator

warnings.filterwarnings('ignore')

# ----------------- UI -----------------
st.set_page_config(page_title="Trading Assistant", layout="wide")
st.title("📈 Trading Assistant")

tabs = st.tabs(["📡 Prediction API Test", "📑 Trade Calculator", "📊 Trade Performance"])

# ----------------- Tab 1: API Test -----------------
with tabs[0]:
    st.subheader("Test API for a Single Ticker")
    ticker = st.text_input("Ticker", "AAPL")
    threshold = st.slider("Threshold", 0.0, 1.0, 0.5, 0.01)

    if st.button("Run Prediction", key="api_test"):
        try:
            # Call API (or directly import from api_app)
            from script.trade_calculator import request_to_api_loacal_host
            result = request_to_api_loacal_host(ticker, threshold)

            if result[0] is None:
                st.error("Prediction failed.")
            else:
                (ticker, type_, ticker_proba, ticker_predicted_change, 
                 ticker_predicted_var, confidence, current_price, 
                 target_price, sl_price, aic_score) = result

                st.write("✅ Prediction Result")
                st.json({
                    "Ticker": ticker,
                    "Type": type_,
                    "Probability": ticker_proba,
                    "Predicted Change": ticker_predicted_change,
                    "Predicted Variance": ticker_predicted_var,
                    "Confidence": confidence,
                    "Current Price": current_price,
                    "Target Price": target_price,
                    "SL Price": sl_price,
                    "AIC Score": aic_score
                })
        except Exception as e:
            st.error(f"Error: {e}")

# ----------------- Tab 2: Trade Calculator -----------------
with tabs[1]:
    st.subheader("Trade Calculator")
    tickers_ns = get_ticker_nse()
    sample_ticker = st.number_input("Number of tickers to sample", 1, len(tickers_ns), 5)
    risk_rate = st.number_input("Risk Ratio", 0.0, 10.0, 1.0, 0.1)

    if st.button("Run Trade Calculator"):
        tickers = random.sample(tickers_ns, sample_ticker)
        results_list = []

        with st.spinner("Fetching predictions..."):
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                results = list(executor.map(request_to_api_loacal_host, tickers, [risk_rate]*len(tickers)))

            for res in results:
                if res[0] is None:
                    continue
                (ticker, type_, ticker_proba, ticker_predicted_change, 
                 ticker_predicted_var, confidence, current_price, 
                 target_price, sl_price, aic_score) = res

                results_list.append({
                    "Ticker": ticker,
                    "Type": type_,
                    "Probability": ticker_proba,
                    "Predicted Change": ticker_predicted_change,
                    "Predicted Variance": ticker_predicted_var,
                    "Confidence": confidence,
                    "Current Price": current_price,
                    "Target Price": target_price,
                    "SL Price": sl_price,
                    "AIC Score": aic_score
                })

        if results_list:
            df = pd.DataFrame(results_list)
            st.dataframe(df)

            # Save CSV
            TRADE_DATA_FOLDER = "trade_data"
            os.makedirs(TRADE_DATA_FOLDER, exist_ok=True)
            filename = f"trades-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv"
            filepath = os.path.join(TRADE_DATA_FOLDER, filename)
            df.to_csv(filepath, index=False)
            st.success(f"Saved to {filepath}")
            st.download_button("Download CSV", df.to_csv(index=False), file_name=filename)

# ----------------- Tab 3: Trade Performance -----------------
with tabs[2]:
    st.subheader("Trade Performance Calculator")
    uploaded_file = st.file_uploader("Upload Trade Data (CSV)", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df.dropna(inplace=True) 
        st.write("Uploaded Data", df)

        # Apply trade performance
        def apply_trade_performance(row):
            return trade_performance_calculator(
                ticker=row["Ticker"],
                last_price=row["Current Price"],
                stop_loss=row["SL Price"],
                target_price=row["Target Price"],
                long=True if row["Type"].lower() == "long" else False,
                executing_interval=5,
                executing_interval_price=0.2
            )

        with st.spinner("Calculating performance..."):
            performance_results = df.apply(apply_trade_performance, axis=1)
            performance_df = pd.DataFrame(list(performance_results))

        st.write("Performance Results", performance_df)

        # Save + download
        FOLDER_NAME = "trade_data"
        os.makedirs(FOLDER_NAME, exist_ok=True)
        filename = f"trade_performance-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv"
        filepath = os.path.join(FOLDER_NAME, filename)
        performance_df.to_csv(filepath, index=False)
        st.success(f"Saved to {filepath}")
        st.download_button("Download Performance CSV", performance_df.to_csv(index=False), file_name=filename)
