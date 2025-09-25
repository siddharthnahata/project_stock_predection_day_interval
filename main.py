from script.trade_calculator import request_to_api_loacal_host
from script.tickers import tickers_ns
import os
import pandas as pd
import concurrent.futures
import random
from datetime import datetime

TRADE_DATA_FOLDER = "trade_data"
TRADE_DATA_FILE_NAME = f"trades-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv"
TRADE_DATA_PATH = f"{TRADE_DATA_FOLDER}/{TRADE_DATA_FILE_NAME}"

os.makedirs(TRADE_DATA_FOLDER, exist_ok=True)

sample_ticker = None
while sample_ticker is None:
    try:
        user_input = input("Enter the number of ticker to be sampled. ")
        sample_ticker = int(user_input)
    except ValueError:
        print("Invalid input. Please enter a valid number.")


tickers = random.sample(tickers_ns, sample_ticker)

risk_rate = None
while risk_rate is None:
    try:
        user_input = input("Enter the risk ratio. ")
        risk_rate = float(user_input)
    except ValueError:
        print("Invalid input. Please enter a valid number.")

results_list = []

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(request_to_api_loacal_host, tickers, [risk_rate]*len(tickers)))

for i, ((ticker, type, ticker_proba, ticker_predicted_change, ticker_predicted_var, confidence, current_price, target_price, sl_price, aic_score)) in enumerate(results, start=1):
    if ticker is None:
        print(f"Failed for one candidate {i}/{len(tickers)}")
        continue
    results_list.append({
        "Ticker": ticker,
        "Type": type,
        "Probability": ticker_proba,
        "Predicted Change": ticker_predicted_change,
        "Predicted Variance": ticker_predicted_var,
        "Confidence": confidence,
        "Current Price": current_price,
        "Target Price": target_price,
        "SL Price": sl_price,
        "AIC Score": aic_score
    })
    print(f"Sucessfully fetched and processed data for {ticker}, {i}/{len(tickers)}")

# Create DataFrame and save to CSV
data = pd.DataFrame(results_list)

try:
    data.to_csv(TRADE_DATA_PATH, index=False)
    print("Sucessfully savec the data on", TRADE_DATA_PATH)
except Exception as e:
    print("Error while saving: ", e)