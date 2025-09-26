from tickers import get_ticker_nse # list of the tickers
from script.model_data_fetch import model_data
from script.classifier_model_training import stack_models
from datetime import datetime
import joblib
import os

MODEL_FOLDER = "model"
os.makedirs(MODEL_FOLDER, exist_ok=True)
MODEL_NAME = f"stock_prediction{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pkl"
MODEL_PATH = os.path.join(MODEL_FOLDER, MODEL_NAME)

tickers_ns = get_ticker_nse()

# loading/getting model data to fit in the model
X, y, cat_cols, num_cols = model_data(ticker_list=tickers_ns)

clf = stack_models(X, y, num_cols, cat_cols) # will return fitted model

joblib.dump(clf, MODEL_PATH)

print("Final model being build sucessfully and saved data")