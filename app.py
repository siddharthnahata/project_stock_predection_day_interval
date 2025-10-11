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
st.title("Trading Assistant")

tabs = st.tabs(["Prediction API Test", "Trade Calculator", "Trade Performance"])

# ----------------- Tab 1: API Test -----------------
with tabs[0]:
    st.subheader("Test API for a Single Ticker")
    ticker = st.text_input("Ticker", "TCS.NS")
    threshold = st.slider("Threshold", 0.0, 1.0, 0.5, 0.01)
    st.write("The value should be betweem 0-1, which representing the confidence where lower leans to short trades and higher leans to long trades.")
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

                st.write("Prediction Result")
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
    tickers = st.multiselect(
        label="Select one or more tickers:",
        options=tickers_ns,
        placeholder="Search or select tickers..."
    )
    risk_rate = st.number_input("Risk Ratio", 0.0, 10.0, 1.0, 0.1)

    st.write("Note: This function should only be runned before the trading hours.")
    if st.button("Run Trade Calculator"):
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
            filename = f"trades-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv"
            st.success(f"Successfully Completed the process, Download the data from the button.")
            st.download_button("Download CSV", df.to_csv(index=False), file_name=filename)

# ----------------- Tab 3: Trade Performance -----------------
with tabs[2]:
    st.subheader("Trade Performance Calculator")
    uploaded_file = st.file_uploader("Upload Trade Data (CSV)", type=["csv"])
    st.write("Note: This function only support a specific format which is generated from the Trade Calculator tab and should be runned after the trading hours.")

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
        filename = f"trade_performance-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv"
        st.success(f"Successfully Completed the process, Download the data from the button.")
        st.download_button("Download Performance CSV", performance_df.to_csv(index=False), file_name=filename)

