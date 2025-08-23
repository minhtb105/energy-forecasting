import pandas as pd
from sklearn.model_selection import train_test_split
from data_prep import load_data, encode_season
from utils import add_calendar_features
from models import run_lazy_regressor
from evaluation import evaluate
from mlflow_utils import setup_mlflow, log_model_results

# setup mlflow
setup_mlflow(experiment_name="gefcom2012_baseline")

# load data
train_df, test_df = load_data(
    "data/global_energy_forcasting_2012/processed/train.csv",
    "data/global_energy_forcasting_2012/processed/test.csv"
)

train_df.drop(["Unnamed: 0"], axis=1, inplace=True)
test_df.drop(["Unnamed: 0"], axis=1, inplace=True)

# feature engineering
train_df = add_calendar_features(train_df)
test_df = add_calendar_features(test_df)

train_df, test_df = encode_season(train_df, test_df)

y_train = train_df["load"]
X_train = train_df.drop(["load"], axis=1)

X_tr, X_val, y_tr, y_val = train_test_split(
    X_train, y_train, test_size=0.2, shuffle=False
)

# run LazyRegressor
models, predictions, model_dict = run_lazy_regressor(X_tr, X_val, y_tr, y_val)

# log results
for model_name, model in model_dict.items():
    y_pred_val = model.predict(X_val)
    metrics = evaluate(y_val, y_pred_val)
    params = {"num_train_samples": len(X_tr), "num_val_samples": len(X_val)}
    log_model_results(model_name, model, metrics, params)
