from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
from script.model_data_fetch import safe_fetch
from script.classifier_model_training import predict_with_threshold
from script.train_volatility_prediction import volatility_predict

MODEL_FILE_NAME = "stock_prediction.pkl"
MODEL_FOLDER = "model"
MODEL_PATH = f"{MODEL_FOLDER}/{MODEL_FILE_NAME}"

model = joblib.load(MODEL_PATH)

app = FastAPI(title="ML API with Automated feature fetech")

class InputData(BaseModel):
    ticker: str
    threshold: float

def make_json_serializable(obj):
    """
    Recursively convert objects into JSON-serializable formats.

    This function is useful when working with FastAPI / Flask responses or 
    saving data that may include NumPy, Pandas, or other non-serializable objects.

    Handles:
    - dict → ensures keys/values are serializable
    - list/tuple → serializes each element
    - numpy/pandas scalars → converts with `.item()`
    - Pandas Timestamp/Timedelta → converts to string
    - everything else → returned as-is or converted to string

    Args:
        obj: Any object (dict, list, pandas object, numpy scalar, etc.)

    Returns:
        JSON-safe representation of the object.
    """
    if isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(v) for v in obj]
    elif hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            return str(obj)
    elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)
    else:
        return obj

@app.post("/predict")
def predict(data: InputData):
    try:
        # fetching the data from function made and assigning it  
        df, X, _ = safe_fetch(data.ticker)
        last_date = df.index[-1]

        features = X.tail(1) # getting on which prediction is to be made

        direction_pred, direction_proba = predict_with_threshold(
            model, features, data.threshold # trigger model for direction prediction
        )

        direction = "Up" if direction_pred == 1 else "Down"
        
        # garch model prediton for the volatility
        garch_reply = volatility_predict(df)

        # Make sure garch_reply is fully serializable
        garch_reply = make_json_serializable(garch_reply)

        return {
            "Last Date": str(last_date),
            "Direction Prediction": {
                "Direction": direction,
                "Probability": float(direction_proba),
            },
            "Volatility Prediction": garch_reply,
        }
    except Exception as e:
        return {"Error": str(e)}