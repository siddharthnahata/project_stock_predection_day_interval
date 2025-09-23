# 📈 Stock Volatility & Direction Forecasting

## 🔹 Project Overview

This project builds a pipeline to forecast short-term stock movements by combining volatility models (GARCH/EGARCH) with machine learning classifiers.

* Volatility models (GARCH, EGARCH) → estimate the range (magnitude) of tomorrow’s price movement (e.g., “±1.5% expected move”).
 
* Machine learning classifiers (XGBoost, etc.) → predict the direction (Up/Down) of tomorrow’s return.

* Together, they provide a practical trading signal: “Tomorrow stock is likely to move +1.5%” or “Tomorrow stock is likely to drop –2.0%”.

## 🔹 Key Features

1. Data Collection: Stock data retrieved via yfinance.

2. Preprocessing: Returns computed, technical indicators added (RSI, MACD, SMA).

3. Volatility Forecasting:

* Tuned GARCH(1,1) and EGARCH(2,1) with Student’s t distribution.

* Outputs daily volatility forecast (σ) as expected % movement.

* Example: “Tomorrow’s volatility = ±1.48%”.

4. Direction Forecasting:

* ML classifier predicts Up/Down using technical features.

* Accuracy evaluated with train/test split.

5. Combined Signal:

* Volatility gives range size.

* Classifier gives direction.

* Final forecast = Predicted Return = Direction × σ.


## 🔹 Why This Approach

* Returns are noisy → direct regression performs poorly.

* Volatility is predictable → GARCH-family models capture clustering of large/small moves.

* Direction is learnable → classifiers achieve >50% accuracy on up/down movement.

* Combination mimics industry practice (hedge funds and risk desks).

## 🔹 Results

* Typical Apple daily volatility forecast ≈ 1–2%, consistent with real market behavior.

* Forecasts capture volatility clustering (calm vs high-risk periods).

* Direction classifier provides a probabilistic edge (>50% win rate).

* Outlier moves (e.g., +3.6% in one day) remain rare but within model’s confidence bands.

## 🔹 Limitations

* GARCH models forecast risk, not direction.

* Daily return prediction is inherently noisy.

* Yahoo Finance (yfinance) has a 1-day delay for daily candles → intraday data may be needed for real-time use.


## Tech Stack Used

1. Python
2. FastAPI
3. Machine learning algorithms

## Infrastructure required

* Local Host 

## How to run

Step 1. Cloning the repository.

```

git clone https://github.com/siddharthnahata/project_stock_predection_day_interval.git

```

Step 2. Create a python environment.

```

python3 -m venv venv

```

```
.venv\Scripts\activate.bat

```

Step 3. Install the requirements

```

pip install -r requirements.txt

```

Step 4. Run the application server

```

python run.py

```

Step 5. Prediction application

```

http://localhost:5000/predict

```

## Usage Tutorial

See [USAGE.md](USAGE.md) for step-by-step instructions and example API calls.

## Classifier Model Training
* If you want to train model on specific industry or ticker update ticker.py under scripts
* After updaing tickers according to yahoo finance API. Also can modify or tune the model from scripts/classifier_model_training.py run following commands to train your model.
Command Promt (windows)
```
cd project_stock_predection_day_interval
python scripts\train.py
``` 
* Can look for Script Summary point 1-3 for more details regarding the process.

## Models Used

* [GARCH Models](https://pyflux.readthedocs.io/en/latest/garch.html)
* [XGBoostClassifier](https://xgboost.readthedocs.io/en/stable/)
* [LGBMClassifier](https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.LGBMClassifier.html)
* [StackingClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html)

**Components** : Contains all components of Machine Learning Project

- Data Fetching
- Data Ingestion
- Data Validation
- Data Transformation
- Model Trainer
- Model Evaluation
- Model Pusher

## Notebook Summary
1. We created a testing_models_regression_for_volatility.ipynb under notebook folder for garch model prepration.
>>*1.1*. We made a way to fetch data from yahoo finance pytho api yfinance
>>*1.2*. Training model
Note:
for our project we will have to train the garch model everytime for new request. Which it is not to expensive as the model are optimized and fast. 
2. Created a classifier_model_building_and_loading_data.ipynb for the classification model which will give up or down signal.
>>*2.1*. We made a function that fetchs the data.
>>*2.2*. We will difine pipeline and sperate feature as numerical and categorical for scaling pupose.
>>*2.3*. Hyper tuning the best model after getting the best base model.

## Scripts Summary
1. Creating a script that handles data fetching and feature creation and returns it for the classification model building in the data folder. and a ticker.py which contains all the ticker which model is being trained on. (can be modified as per need of the user)
2. classification model script created this handles the model building part.
3. Created a train.py file which compile data fetching and train the model.
4. created a garch script which predicts volatility.
5. some of the function are not covered in the summary which are important too can look script for the description


## Conclusion

This project demonstrates a practical approach to short-term stock forecasting by combining volatility modeling (GARCH/EGARCH) with machine learning classifiers for direction prediction. The pipeline provides both the expected magnitude and direction of price movement, offering actionable insights for traders and analysts. While the models capture key market behaviors such as volatility clustering and directional tendencies, users should be aware of the inherent unpredictability and noise in financial markets. The modular design allows for easy adaptation to different tickers, industries, and model improvements.

## Disclaimer
This project is for educational and informational purposes only and does not constitute financial advice or investment recommendations. Forecasts and predictions generated by this tool are based on historical data and statistical models, which cannot guarantee future results. Trading and investing in financial markets involve significant risk, including the loss of your invested capital. Always conduct your own research and consult with a qualified financial advisor before making investment decisions. The author assumes no responsibility for any financial losses or damages resulting from the use of this project.