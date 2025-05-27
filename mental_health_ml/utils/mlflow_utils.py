import mlflow
import os

# Default values, can be overridden by environment variables
DEFAULT_MLFLOW_TRACKING_URI = "http://localhost:5000" # Change if your server is usually elsewhere
DEFAULT_EXPERIMENT_NAME = "MentalHealthApp_Models"

def initialize_mlflow_tracking(
    tracking_uri: str = None,
    experiment_name: str = None
):
    """
    Initializes MLflow tracking URI and sets the active experiment.

    Args:
        tracking_uri (str, optional): The MLflow tracking server URI.
            If None, attempts to get from MLFLOW_TRACKING_URI env var,
            then defaults to DEFAULT_MLFLOW_TRACKING_URI.
        experiment_name (str, optional): The name of the MLflow experiment.
            If None, attempts to get from MLFLOW_EXPERIMENT_NAME env var,
            then defaults to DEFAULT_EXPERIMENT_NAME.
    """
    # Determine Tracking URI
    if tracking_uri is None:
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", DEFAULT_MLFLOW_TRACKING_URI)

    # Determine Experiment Name
    if experiment_name is None:
        experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", DEFAULT_EXPERIMENT_NAME)

    try:
        mlflow.set_tracking_uri(tracking_uri)
        current_tracking_uri = mlflow.get_tracking_uri() # Get what MLflow actually set
        print(f"MLflow tracking URI set to: {current_tracking_uri}")

        # Check if experiment exists, otherwise create it
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            print(f"Experiment '{experiment_name}' not found. Creating it.")
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"Experiment '{experiment_name}' created with ID: {experiment_id}")
        else:
            experiment_id = experiment.experiment_id
            print(f"Experiment '{experiment_name}' already exists with ID: {experiment_id}.")

        mlflow.set_experiment(experiment_name)
        print(f"Active experiment set to: '{experiment_name}'")

    except Exception as e:
        print(f"ERROR initializing MLflow: {e}")
        print(f"  Attempted Tracking URI: {tracking_uri}")
        print(f"  Attempted Experiment Name: {experiment_name}")
        print("  Please ensure:")
        print("    1. The MLflow server is running and accessible at the specified URI.")
        print("    2. The PostgreSQL database (if used) is correctly configured and accessible by the MLflow server.")
        print("    3. If using environment variables (MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME), they are set correctly.")
        # Optionally, re-raise the exception or handle it as needed
        # raise