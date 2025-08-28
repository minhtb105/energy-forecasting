import mlflow
import mlflow.sklearn

def setup_mlflow(experiment_name="gefcom2012_baseline", tracking_uri="sqlite:///mlflow.db"):
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

def log_model_results(model_name, model, metrics, params, name="model", input_example=None):
    with mlflow.start_run(run_name=model_name):
        for k, v in metrics.items():
            mlflow.log_metric(k, v)
            
        for k, v in params.items():
            mlflow.log_param(k, v)
        
        mlflow.sklearn.log_model(
            model,
            artifact_path=name,
            input_example=input_example
        )
