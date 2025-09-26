import pandas as pd
import requests
import io

# Download the list of all equity stocks from NSE


def get_ticker_nse():
    URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    "This Function will only work for above link"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv"
    }
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    tickers = df['SYMBOL'].apply(lambda x: f"{x}.NS").tolist()
    return tickers

