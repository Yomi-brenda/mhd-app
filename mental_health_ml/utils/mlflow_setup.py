# mlflow_setup.py
import mlflow

def setup_mlflow():
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("mental_health_support")
    
if __name__ == "__main__":
    setup_mlflow()
    print("MLflow tracking initialized")