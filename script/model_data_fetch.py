import pandas as pd 
import yfinance as yf
import ta
import concurrent.futures

# this function can be used when updating the model and in production model updating
def ticker_data_fetch(ticker: str, interval: str, period: str, feature_cal: bool):
    try:
        t = yf.Ticker(ticker)

        # Fetch price history
        df = t.history(interval=interval, period=period)
        if df.empty:
            print(f"[WARN] No data for {ticker}")
            return None, None, None       

        if feature_cal:
            df.index = df.index.strftime("%Y-%m-%d")
            # Technical indicators

        # Technical indicators
            df["return_1d"] = df["Close"].pct_change(1)
            df["return_7d"] = df["Close"].pct_change(7)
            df["return_30d"] = df["Close"].pct_change(30)
            df["return_180d"] = df["Close"].pct_change(180)
            df["return_365d"] = df["Close"].pct_change(365)
            df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            df['macd'] = ta.trend.MACD(df['Close']).macd()
            df["stoch"] = ta.momentum.StochasticOscillator(df["High"], df["Low"], df["Close"]).stoch()
            df["roc"] = ta.momentum.ROCIndicator(df["Close"]).roc()
            df["williams_r"] = ta.momentum.WilliamsRIndicator(df["High"], df["Low"], df["Close"]).williams_r()
            df["realized_vol_5"] = df["return_1d"].rolling(5).std()
            df["rolling_std_5"]  = df["Close"].rolling(5).std()
            df["rolling_skew_5"] = df["Close"].rolling(5).skew()
            df["rolling_kurt_5"] = df["Close"].rolling(5).kurt()
            df['sma5'] = df['Close'].rolling(5).mean()
            df['sma10'] = df['Close'].rolling(10).mean()
            df['sma20'] = df['Close'].rolling(20).mean()
            df['sma50'] = df['Close'].rolling(50).mean()
            df['sma100'] = df['Close'].rolling(100).mean()
            df['sma200'] = df['Close'].rolling(200).mean()
            df["vwap"] = (df["Volume"] * (df["High"]+df["Low"]+df["Close"])/3).cumsum() / df["Volume"].cumsum()
            df["volume_change"] = df["Volume"].pct_change()

            # Safe sector info
            sector = t.info.get('sector', 'Unknown')
            df['sector'] = sector

            df.index = pd.to_datetime(df.index)
            df['day_of_week'] = df.index.day_name()
            
            df['ticker'] = ticker

            # Target (next-day return direction)
            df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

            # Drop missing rows
            df.dropna(inplace=True)

            # Features & labels
            X = df[['return_1d', 'return_7d', 'return_30d', 'return_180d', 'return_365d', 'stoch', 'roc', 'williams_r', 'realized_vol_5', 'rolling_std_5', 'rolling_skew_5', 'rolling_kurt_5', 'rsi','macd','sma5','Volume', 'sma10','sma20','sma50','sma100','sma200','sector', 'vwap', 'volume_change', 'day_of_week', 'ticker']]
            y = df['target']
            return df, X, y
        else:
            return df, None, None

    except Exception as e:
        print(f"[ERROR] Failed for {ticker}: {e}")
        return None, None, None
    
# Worker wrapper for safe execution
def safe_fetch(ticker: str, interval: str, period: str, feature_cal: bool):
    try:
        return ticker_data_fetch(ticker, interval, period, feature_cal)
    except Exception as e:
        print(f"[ERROR] {ticker}: {e}")
        return None

def model_data(ticker_list, interval="1d", period="5y", feature_cal=True):
    main_base_df_list = []
    X_list = []
    y_list = []

    args = [(ticker, interval, period, feature_cal) for ticker in ticker_list]
    # Run in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(lambda p: safe_fetch(*p), args))

    # Collect results
    for i, result in enumerate(results, start=1):
        if result is None or result[0] is None or result[1] is None or result[2] is None:
            print(f"{i}/{len(ticker_list)} skipped")
            continue
        df_fetch, X_fetch, y_fetch = result
        main_base_df_list.append(df_fetch)
        X_list.append(X_fetch)
        y_list.append(y_fetch)
        print(f"{i}/{len(ticker_list)} done")

    main_base_df = pd.concat(main_base_df_list, axis=0).reset_index(drop=True)
    X = pd.concat(X_list, axis=0).reset_index(drop=True)
    y = pd.concat(y_list, axis=0).reset_index(drop=True)

    cat_cols = []
    num_cols = []
    for i in X.columns:
        if X[i].dtype == "O":
            cat_cols.append(i)
        else:
            num_cols.append(i)
    print("Categorical Features : ", cat_cols)
    print("Numerical Features : ", num_cols)
    return X, y, cat_cols, num_cols