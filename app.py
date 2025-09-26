import math
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
from script.model_data_fetch import safe_fetch
from script.classifier_model_training import predict_with_threshold
from script.train_volatility_prediction import volatility_predict
import os

import warnings
warnings.filterwarnings('ignore')

MODEL_FOLDER = "model"
model_files = [f for f in os.listdir(MODEL_FOLDER) if f.endswith('.pkl')]
if not model_files:
    raise FileNotFoundError("No .pkl model files found in the model folder.")

print("Available models:")
for idx, fname in enumerate(model_files, 1):
    print(f"{idx}: {fname}")

selected = None
while selected is None:
    try:
        user_input = input("Enter the number of the model to use: ")
        selected_idx = int(user_input) - 1
        if 0 <= selected_idx < len(model_files):
            selected = model_files[selected_idx]
        else:
            print("Invalid selection. Try again.")
    except Exception:
        print("Invalid input. Please enter a valid number.")
MODEL_PATH = os.path.join(MODEL_FOLDER, selected)

model = joblib.load(MODEL_PATH)

print("Starting up the API model....")

app = FastAPI(title="ML API with Automated feature fetech")

class InputData(BaseModel):
    ticker: str
    threshold: float

def make_json_serializable(obj):
    """
    Recursively convert objects into JSON-serializable formats.
    Also converts NaN and infinite values to None.
    """
    if isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(v) for v in obj]
    elif hasattr(obj, "item"):
        try:
            value = obj.item()
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                return None
            return value
        except Exception:
            return str(obj)
    elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, np.generic):
        value = obj.item()
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        return value
    else:
        return obj

@app.post("/predict")
def predict(data: InputData):
    try:
        # fetching the data from function made and assigning it  
        print("Starting fetching data process...")
        df, X, _ = safe_fetch(
            data.ticker,
            interval="1d",
            period="5y",
            feature_cal=True,
        )

        last_date = df.index[-1]

        print("Aligning the feature to predict....")
        features = X.tail(1) # getting on which prediction is to be made

        print("Sending the data for clf model.")
        direction_pred, direction_proba = predict_with_threshold(
            model, features, data.threshold # trigger model for direction prediction
        )

        direction = "Up" if direction_pred == 1 else "Down"
        
        print("Sending the data for Garch model.")
        # garch model prediton for the volatility
        garch_reply = volatility_predict(df)

        # Make sure garch_reply is fully serializable
        garch_reply = make_json_serializable(garch_reply)

        print("Sucessfull")
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