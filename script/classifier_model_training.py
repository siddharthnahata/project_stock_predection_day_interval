import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.ensemble import StackingClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier


def predict_with_threshold(model, features, threshold):
    """ 
        this function it for predicting on custom thershold limit.
    """
    
    # Get probabilities for class 1
    proba = model.predict_proba(features)[:, 1]

    # Apply threshold
    y_pred = np.where(proba >= threshold, 1, 0)
    return y_pred, proba



def stack_models(X, y, num_cols, cat_cols):
    """
        this code is where classification model is being build can be modifed as per you research.
    """

    # handling values
    # Numeric columns
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.dropna()   # drop rows where any feature is NaN (was inf before)

    # Also align y with X (important!)
    y = y.loc[X.index]
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat_cols)
        ]
    )

    # Base models
    base_models = [
        ("xgb", XGBClassifier(use_label_encoder=False, eval_metric="error")),
        ("lgbm", LGBMClassifier()),
        ("cat", CatBoostClassifier(verbose=0, random_state=random_state))
    ]

    # Meta-model
    meta_model = LogisticRegression(max_iter=2000)

    # Stacking Classifier
    clf = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("stack", StackingClassifier(
            estimators=base_models,
            final_estimator=meta_model,
            cv=5
        ))
    ])

    clf.fit(X, y)
    return clf
    