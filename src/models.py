from lazypredict.Supervised import LazyRegressor

def run_lazy_regressor(X_tr, X_val, y_tr, y_val, verbose=0):
    reg = LazyRegressor(verbose=verbose, ignore_warnings=False, custom_metric=None)
    models, predictions = reg.fit(X_tr, X_val, y_tr, y_val)
    model_dict = reg.provide_models(X_tr, X_val, y_tr, y_val)
    
    return models, predictions, model_dict
