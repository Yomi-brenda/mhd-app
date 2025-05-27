# mental_health_ml/training/train_emotion_model.py

import mlflow
# Assuming 'utils' is a sibling directory to 'training'
# and your script is run from the project root 'mental_health_ml/'
# or your PYTHONPATH is set up correctly.
from utils.mlflow_utils import initialize_mlflow_tracking

# --- MLflow Setup ---
# Call the initialization function at the beginning of your script
# You can override the defaults if needed for this specific script:
# initialize_mlflow_tracking(tracking_uri="http://custom-server:port", experiment_name="Specific_Emotion_Experiments")
initialize_mlflow_tracking() # Uses defaults or environment variables

# --- Your Model Training Code ---
def train_model():
    # Example: Start an MLflow run
    with mlflow.start_run(run_name="EmotionModel_BERT_Run1"):
        print(f"Current MLflow Run ID: {mlflow.active_run().info.run_id}")
        print(f"Current MLflow Experiment ID: {mlflow.active_run().info.experiment_id}")

        # Log parameters
        mlflow.log_param("model_type", "BERT-base-uncased")
        mlflow.log_param("learning_rate", 5e-5)
        # ... more params

        # Simulate training
        print("Training model...")
        train_loss = 0.5
        val_accuracy = 0.85

        # Log metrics
        mlflow.log_metric("train_loss", train_loss, step=1)
        mlflow.log_metric("val_accuracy", val_accuracy, step=1)

        # Log a dummy model artifact (replace with actual model logging)
        with open("dummy_model.txt", "w") as f:
            f.write("This is a dummy model.")
        mlflow.log_artifact("dummy_model.txt", artifact_path="model_files")

        print("Model training finished and artifacts logged.")

if __name__ == "__main__":
    print("Starting training script...")
    train_model()
    print("Training script finished.")