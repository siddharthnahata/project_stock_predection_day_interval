import numpy as np
import pandas as pd
from arch import arch_model

def qlike_loss(realized_var, predicted_var):
    return np.mean((realized_var / predicted_var) - np.log(realized_var / predicted_var) - 1)

def volatility_predict(df: pd.DataFrame):
    try:    
        returns = 100 * df['Close'].pct_change().dropna()
    except Exception as e:
        return f"Model Failed while computing. {e}"
    
    best_aic, best_model, best_params, best_qlike = 1e10, None, None, None

    for vol in ["Garch", "EGARCH", "GJR-GARCH"]:
        for dist in ["normal", "t", "skewt"]:
            for p in range(1,3):
                for q in range(1,3):
                    try:
                        model = arch_model(returns, vol=vol, p=p, q=q, dist=dist, mean="Constant")
                        res = model.fit(disp="off")
                        forecast = res.forecast(horizon=1)
                        predicted_var = forecast.variance.iloc[-1].values
                        realized_var = returns.iloc[-1]**2
                        qlike = qlike_loss(np.array([realized_var]), predicted_var)
                        
                        if res.aic < best_aic:
                            best_aic = res.aic
                            best_model = res
                            best_params = [vol, dist, p, q]
                            best_qlike = qlike
                    except:
                        continue
    
    if best_model is None:
        return "failed to build model."

    try:
        model = arch_model(returns, vol=best_params[0], p=best_params[2], q=best_params[3], dist=best_params[1], mean="Constant")
        res = model.fit(disp="off")

        # Forecast next 5 days ahead
        forecast = res.forecast(horizon=1)

        # Extract variance forecast
        predicted_var = forecast.variance.iloc[-1].values
        predicted_vol = np.sqrt(predicted_var)
    except Exception as e:
        return f"Error while training/predicting: {e}"
    
    # setting model prediction in a dictionary
    model_prediction = {
        "Predicted Change/Volume": predicted_vol,
        "Predicted Variance": predicted_var,
    }

    # setting model metrics in dictionary
    model_description = {
        "Model AIC": best_aic,
        "Best Params": best_params,
        "QLIKE Score": best_qlike,
    }

    # combined both in one dictionary for flexiable return
    model_reply = {
        "Prediction": model_prediction,
        "Model Description": model_description,
    }

    return model_reply
