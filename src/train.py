import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from data_prep import load_data, encode_season
from utils import add_cyclical_time_features, add_calendar_features
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

# feature engineering
train_df = add_calendar_features(train_df)
test_df = add_calendar_features(test_df)
train_df = add_cyclical_time_features(train_df, False)
test_df = add_cyclical_time_features(test_df, False)

train_df, test_df = encode_season(train_df, test_df)

y_train = train_df["load"]
X_train = train_df.drop(["load", "date_time"], axis=1)

X_tr, X_val, y_tr, y_val = train_test_split(
    X_train, y_train, test_size=0.2, shuffle=False
)

scale_cols = ["proxy_temp", "CDD", "HDD", "lag_1", "lag_24", "lag_168", 
    "roll_mean_24", "roll_mean_168"]

X_tr[scale_cols] = scaler.fit_transform(X_tr[scale_cols])
X_val[scale_cols] = scaler.transform(X_val[scale_cols])
test_df[scale_cols] = scaler.transform(test_df[scale_cols])

sample_sizes = [5000, 10000, 20000, 40000]

for n in sample_sizes:
    # Lấy sample từ train/val
    X_tr_sample = X_tr.sample(n=n, random_state=42)
    y_tr_sample = y_tr.loc[X_tr_sample.index]

    X_val_sample = X_val.sample(n=2000, random_state=42)
    y_val_sample = y_val.loc[X_val_sample.index]

    # run LazyRegressor
    models, predictions, model_dict = run_lazy_regressor(X_tr_sample, 
                                                        X_val_sample, 
                                                        y_tr_sample, y_val_sample)

    # log results
    for model_name, model in model_dict.items():
        y_pred_val = model.predict(X_val_sample)
        metrics = evaluate(y_val_sample, y_pred_val, X_val_sample.shape[1])
        params = {"num_train_samples": len(X_tr_sample), "num_val_samples": len(X_val_sample)}
        log_model_results(model_name, model, metrics, params)