## Response Summary

The API response provides a comprehensive forecast for the next trading day, combining both direction and volatility predictions:

- **Last Date**:  
  The most recent date for which the prediction is made.

- **Direction Prediction**:  
  - **Direction**: Indicates whether the model expects the stock price to go "Up" or "Down" on the next day.
  - **Probability**: The model’s confidence in its direction prediction, as a probability between 0 and 1.

- **Volatility Prediction**:  
  - **Prediction**:  
    - **Predicted Change/Volume**: The expected magnitude of price movement (volatility) for the next day, as estimated by the volatility model.
    - **Predicted Variance**: The statistical variance of the predicted price change.
  - **Model Description**:  
    - **Model AIC**: The Akaike Information Criterion, a measure of model quality (lower is better).
    - **Best Params**: The best parameters found for the volatility model (e.g., model type, distribution, and order).
  - **QLIKE Score**: A quantitative metric evaluating the accuracy of the volatility forecast (lower is better).

**Interpretation:**  
This response allows users to see both the expected direction (up or down) and the likely size of the move (volatility), along with model diagnostics. This dual insight is valuable for making informed trading or risk management decisions, but users should always consider the inherent uncertainty and risk in financial predictions.

## Threshold Input Summary

The `threshold` input in the API request body allows users to set the minimum probability required for the model to make a confident direction prediction (Up/Down). It acts as a filter for prediction certainty:

- **How it works:**  
  - If the model's predicted probability for "Up" or "Down" is greater than or equal to the threshold, the direction is returned.
  - If the probability is below the threshold, the model may abstain from making a prediction or indicate low confidence (depending on implementation).

- **Why use it:**  
  - A higher threshold (e.g., 0.7) means the model will only predict when it is more confident, reducing false signals but possibly giving fewer predictions.
  - A lower threshold (e.g., 0.5) allows more predictions, but with lower average confidence.

- **Example:**  
  ```json
  {
    "ticker": "TCS.NS",
    "threshold": 0.52
  }
  ```
  This means the model will only predict "Up" or "Down" if its probability is at least 52%.

**Tip:**  
Adjust the threshold based on your risk tolerance and desired trade-off between prediction frequency and confidence.