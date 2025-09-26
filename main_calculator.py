import os
import pandas as pd
from script.trade_performance import trade_performance_calculator
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

FOLDER_NAME = "trade_data"
os.makedirs(FOLDER_NAME, exist_ok=True)
FILE_NAME = f"trade_performance{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv"
FILE_PATH = os.path.join(FOLDER_NAME, FILE_NAME)

data_folder = None
while data_folder is None:
    try:
        user_input = input("Please enter the path where trade data is present: ")
        if os.path.exists(path=user_input):
            data_folder = user_input
        else:
            print("Path does not exist. Please try again.")
    except Exception as e:
        print("Error: ", e)

data_file_name = None
while data_file_name is None:
    try:
        user_input = input("Enter the file name of trade book: ")
        if user_input.endswith(".csv"):
            data_file_name = user_input
        else:
            print("Only .csv and .xlsx files supported, Please try again.")
    except Exception as e:
        print("Error: ", e)

data_path = f"{data_folder}/{data_file_name}"

df = pd.DataFrame()
if data_path.endswith(".csv"):
    df = pd.read_csv(data_path)
elif data_path.endswith(".xlsx"):
    df = pd.read_excel(data_path)

columns_to_find = [
    "Ticker", "Type", "Probability",
    "Predicted Change", "Predicted Variance",
    "Confidence", "Current Price", "Target Price",
    "SL Price", "AIC Score"
]

for col in df.columns:
    if col not in columns_to_find:
        print(f"Column '{col}' not found please refer template.")

df.dropna(inplace=True)
def apply_trade_performance(row):
    return trade_performance_calculator(
        ticker=row["Ticker"],
        last_price=row["Current Price"],
        stop_loss=row["SL Price"],
        target_price=row["Target Price"] if "Target Price" in row else row["Target"],  # adjust as per your column name
        long=True if row["Type"].lower() == "long" else False,
        executing_interval=5,  # or any value you want
        executing_interval_price=0.2  # or any value you want
    )

# Apply the function to each row and collect results
performance_results = df.apply(apply_trade_performance, axis=1)

# Convert results to DataFrame if you want to save or analyze
performance_df = pd.DataFrame(list(performance_results))

# Optionally, save to CSV
try:
    performance_df.to_csv(FILE_PATH, index=False)
    print("Sucessfully savec the data on", FILE_PATH)
except Exception as e:
    print("Error while saving: ", e)