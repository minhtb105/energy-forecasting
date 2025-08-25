from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

def evaluate(y_true, y_pred, n_features=None):
    rmse = root_mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    n = len(y_true) 
    if n_features is None:
        adj_r2 = None
    else:
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - n_features - 1)
    
    return {
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "adjusted_r2": adj_r2
    }
