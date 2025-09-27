import math
import numpy as np
import pandas as pd
import joblib
import os
import streamlit as st
import warnings

from script.model_data_fetch import safe_fetch
from script.classifier_model_training import predict_with_threshold
from script.train_volatility_prediction import volatility_predict

warnings.filterwarnings('ignore')

# -------------------- Load Models --------------------
MODEL_FOLDER = "model"
model_files = [f for f in os.listdir(MODEL_FOLDER) if f.endswith('.pkl')]
if not model_files:
    st.error("No .pkl model files found in the model folder.")
    st.stop()

st.sidebar.title("⚙️ Model Selection")
selected_model = st.sidebar.selectbox("Choose a model", model_files)
MODEL_PATH = os.path.join(MODEL_FOLDER, selected_model)

@st.cache_resource
def load_model(path):
    return joblib.load(path)

model = load_model(MODEL_PATH)

# -------------------- Helper Functions --------------------
def make_json_serializable(obj):
    """Recursively convert objects into JSON-serializable formats."""
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

# -------------------- Streamlit UI --------------------
st.title("📊 Stock Direction & Volatility Predictor")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, INFY.NS)", "AAPL")
threshold = st.slider("Prediction Threshold", 0.0, 1.0, 0.5, 0.01)

if st.button("Run Prediction"):
    try:
        with st.spinner("Fetching data and running models..."):
            # Fetch historical data
            df, X, _ = safe_fetch(
                ticker,
                interval="1d",
                period="5y",
                feature_cal=True,
            )

            last_date = df.index[-1]

            # Features for prediction
            features = X.tail(1)

            # Classification prediction
            direction_pred, direction_proba = predict_with_threshold(
                model, features, threshold
            )
            direction = "📈 Up" if direction_pred == 1 else "📉 Down"

            # Volatility prediction
            garch_reply = volatility_predict(df)
            garch_reply = make_json_serializable(garch_reply)

        # -------------------- Display Results --------------------
        st.success("Prediction Successful ✅")
        st.subheader("Results")
        st.write(f"**Last Date in Data:** {last_date}")

        direction_proba = float(direction_proba)  # make sure it's scalar
        st.metric("Direction Prediction", direction, f"{direction_proba:.2%}")
        
        st.subheader("Volatility Prediction (GARCH)")
        st.json(garch_reply)

    except Exception as e:
        st.error(f"Error: {e}")
