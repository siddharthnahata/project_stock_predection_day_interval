from tickers import tickers_ns # list of the tickers
from model_data_fetch import model_data
from classifier_model_training import stack_models
import joblib
import os

MODEL_FOLDER = "model"
MODEL_NAME = "stock_prediction.pkl"
MODEL_PATH = f"{MODEL_FOLDER}/{MODEL_NAME}"

os.makedirs(MODEL_FOLDER, exist_ok=True)

# loading/getting model data to fit in the model
X, y, cat_cols, num_cols = model_data(ticker_list=tickers_ns)

clf = stack_models(X, y, num_cols, cat_cols) # will return fitted model

joblib.dump(clf, MODEL_PATH)

print("Final model being build sucessfully and saved data")