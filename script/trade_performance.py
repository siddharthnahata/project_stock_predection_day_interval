from script.model_data_fetch import safe_fetch

def trade_performance_calculator(
        ticker: str,
        last_price: float,
        stop_loss: float,
        target_price: float,
        long: bool,
        executing_interval: int,
        executing_interval_price: float
):
    """
    Simulates trade performance for a given ticker and trade parameters.

    Args:
        ticker: Stock ticker symbol.
        last_price: Intended entry price.
        stop_loss: Stop loss price.
        target_price: Target price.
        long: True for long trade, False for short.
        executing_interval: Number of minutes after open to try to enter trade.
        executing_interval_price: Allowed % deviation from last_price for entry.

    Returns:
        dict with trade outcome and relevant info.
    """
    # Fetch 1-minute data for the day
    df, _, _ = safe_fetch(ticker, interval="1m", period='1d', feature_cal=False)
    if df is None or df.empty:
        return {
            "ticker": ticker,
            "entry_price": "Unable to fetch data(error)",
            "entry_time": "Trade not executed",
            "exit_price": "Trade not executed",
            "exit_time": "Trade not executed",
            "result": "Trade not executed",
            "pnl": 0
        }


    # Only consider the first `executing_interval` minutes for entry
    df_entry_window = df.iloc[:executing_interval]
    entry_price = None
    entry_time = None

    # Calculate allowed price range for entry
    price_upper = last_price * (1 + executing_interval_price / 100)
    price_lower = last_price * (1 - executing_interval_price / 100)

    # Try to find a price within the allowed range in the entry window
    for idx, row in df_entry_window.iterrows():
        price = row['Close']
        if price_lower <= price <= price_upper:
            entry_price = price
            entry_time = idx
            break

    if entry_price is None:
        return {
            "ticker": ticker,
            "entry_price": "Trade not executed",
            "entry_time": "Trade not executed",
            "exit_price": "Trade not executed",
            "exit_time": "Trade not executed",
            "result": "Trade not executed",
            "pnl": 0
        }

    # Now simulate trade from entry_time onward
    df_trade = df.loc[entry_time:]
    hit_target = False
    hit_stop = False
    exit_price = entry_price
    exit_time = entry_time

    for idx, row in df_trade.iterrows():
        price = row['Close']
        if long:
            if price >= target_price:
                hit_target = True
                exit_price = target_price
                exit_time = idx
                break
            elif price <= stop_loss:
                hit_stop = True
                exit_price = stop_loss
                exit_time = idx
                break
        else:
            if price <= target_price:
                hit_target = True
                exit_price = target_price
                exit_time = idx
                break
            elif price >= stop_loss:
                hit_stop = True
                exit_price = stop_loss
                exit_time = idx
                break

    if hit_target:
        result = "target"
        pnl = (exit_price - entry_price) if long else (entry_price - exit_price)
    elif hit_stop:
        result = "stop_loss"
        pnl = (exit_price - entry_price) if long else (entry_price - exit_price)
    else:
        # Neither hit, exit at last available price
        exit_price = df_trade['Close'].iloc[-15]
        exit_time = df_trade.index[-15]
        result = "timeout"
        pnl = (exit_price - entry_price) if long else (entry_price - exit_price)

    return {
        "ticker": ticker,
        "entry_price": entry_price,
        "entry_time": str(entry_time),
        "exit_price": exit_price,
        "exit_time": str(exit_time),
        "result": result,
        "pnl": pnl
    }