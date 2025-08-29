import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
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

tscl = TimeSeriesSplit()

scale_cols = ["proxy_temp", "CDD", "HDD", "lag_1", "lag_24", "lag_168", 
    "roll_mean_24", "roll_mean_168"]

best_models = []

for fold, (train_idx, val_idx) in enumerate(tscl.split(X_train)):
    X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
    y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

    scaler = RobustScaler()

    X_tr[scale_cols] = scaler.fit_transform(X_tr[scale_cols])
    X_val[scale_cols] = scaler.transform(X_val[scale_cols])

    sample_sizes = [40000]

    for n in sample_sizes:
        X_tr_sample = X_tr.iloc[:n] if len(X_tr) >= n else X_tr.copy()
        y_tr_sample = y_tr.loc[X_tr_sample.index]

        X_val_sample = X_val.iloc[:2000] if len(X_val) >= 2000 else X_val.copy()
        y_val_sample = y_val.loc[X_val_sample.index]

        # run LazyRegressor
        models, predictions, model_dict = run_lazy_regressor(X_tr_sample, 
                                                            X_val_sample, 
                                                            y_tr_sample, y_val_sample)

        metrics_dict = {}
        for model_name, model in model_dict.items():
            y_pred_val = model.predict(X_val_sample)
            metrics = evaluate(y_val_sample, y_pred_val, X_val_sample.shape[1])
            metrics_dict[model_name] = metrics

        best_model_name = min(metrics_dict, key=lambda k: metrics_dict[k]["rmse"])
        best_models.append((fold, n, best_model_name, metrics_dict[best_model_name]))
        
        # log best model only
        log_model_results(f"{best_model_name}_fold{fold}_n{n}", 
                          model_dict[best_model_name], 
                          metrics_dict[best_model_name], 
                          {"num_train_samples": n, "num_val_samples": len(X_val_sample)})
        