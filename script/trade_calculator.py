import yfinance as yf
import requests

def ticker_price_fetch(ticker: str):
    """
        this function is to fetch the current available price of ticker on yfinance 
    """
    try:
        t = yf.Ticker(ticker) 
        # Fetch price
        df = t.history(interval="1d", period="1d")
        if df.empty:
            print(f"[WARN] No data for {ticker}")
            return None
        data = df['Close']
        return float(data.values[-1])
    except Exception as e:
        return f"Error Occured while fetching {ticker}"

def target_calculator(price: float, percentage: float, long: bool):
    profit = price * percentage
    return price + profit if long else price - profit

def stop_loss_calculator(price: float, percentage: float, long: bool):
    loss = price * percentage
    return price - loss if long else price + loss

def request_to_api_loacal_host(ticker: str, risk: float):
    # Setting model payload and address
    url = "http://127.0.0.1:5000/predict"
    payload = {
        "ticker": ticker,
        "threshold": 0.5
    }
    try:
        # sending payload using response module
        response = requests.post(url, json=payload)
        print(f"POST Request with Data for ticker {ticker} | Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"API did not return 200 for {ticker}. Response: {response.text}")
            return (ticker, None, None, None, None, None, None, None, None, None)
        try:
            fetched_data = response.json()
        except Exception as e:
            print(f"Failed to decode JSON for {ticker}: {e}")
            return (ticker, None, None, None, None, None, None, None, None, None)

        
       # Defensive extraction with .get and default values
        direction_pred = fetched_data.get("Direction Prediction", {})
        ticker_proba = direction_pred.get("Probability", None)
        if ticker_proba is None:
            print(f"Probability missing for {ticker}")
            return (ticker, None, None, None, None, None, None, None, None, None)

        long = True if ticker_proba > 0.5 else False
        type = "Long" if long else "Short"

        vol_pred = fetched_data.get("Volatility Prediction", {})
        pred = vol_pred.get("Prediction", {})
        ticker_predicted_change = pred.get("Predicted Change/Volume", None)
        ticker_predicted_var = pred.get("Predicted Variance", None)

        if ticker_predicted_change is None or ticker_predicted_var is None:
            print(f"Volatility prediction missing for {ticker}")
            return (ticker, type, ticker_proba, None, None, None, None, None, None, None)

        if ticker_predicted_change < 1.5:
            print(f"Not enough room for trade {ticker}")
            return (ticker, type, ticker_proba, ticker_predicted_change, ticker_predicted_var, None, None, None, None, None)

        model_des = vol_pred.get("Model Description", {})
        qlike_score = model_des.get("QLIKE Score", None)
        aic_score = model_des.get("Model AIC", None)

        # Confidence logic
        confidence = "Low"
        if qlike_score is not None:
            if qlike_score < 1.5:
                if ticker_proba > 0.60 or ticker_proba < 0.40:
                    confidence = "Very High"
                elif ticker_proba > 0.54 or ticker_proba < 0.46:
                    confidence = "High"
                elif ticker_proba > 0.52 or ticker_proba < 0.48:
                    confidence = "Medium"

        current_price = ticker_price_fetch(ticker)
        if current_price is None:
            print(f"Could not fetch current price for {ticker}")
            return (ticker, type, ticker_proba, ticker_predicted_change, ticker_predicted_var, confidence, None, None, None, aic_score)

        # Convert predicted change to decimal
        target_percentage = ticker_predicted_change / 100
        sl_percentage = target_percentage * risk

        sl_price = stop_loss_calculator(price=current_price, percentage=sl_percentage, long=long)
        target_price = target_calculator(price=current_price, percentage=target_percentage, long=long)

        return (ticker, type, ticker_proba, ticker_predicted_change, ticker_predicted_var, confidence, current_price, target_price, sl_price, aic_score)
    except requests.exceptions.RequestException as e:
        print(f"Error during POST request for ticker {ticker}: {e}")
        return (ticker, None, None, None, None, None, None, None, None, None)