# mental_health_ml/training/register_emotion_model.py
import mlflow
import os
from dotenv import load_dotenv
from transformers import AutoConfig, AutoTokenizer, AutoModelForSequenceClassification
import json

# --- Configuration ---
# Set the specific Hugging Face model we are using for GoEmotions
HF_MODEL_NAME = "SamLowe/roberta-base-go_emotions"
# Define a name for this model within our MLflow Model Registry
MLFLOW_REGISTERED_MODEL_NAME = "EmotionDetector_GoEmotions_Pretrained"
# Define the MLflow Experiment where we'll log this
MLFLOW_EXPERIMENT_NAME = "Emotion_Detection_Models"
# --- End Configuration ---

def log_and_register_pretrained_model(model_id: str, experiment_name: str, registered_name: str):
    """
    Logs information about a pre-trained Hugging Face model to MLflow
    and optionally registers it in the Model Registry.
    """
    load_dotenv() # Ensure MLFLOW_TRACKING_URI is loaded
    mlflow.set_experiment(experiment_name)

    run_name = f"Log_Usage_of_{model_id.replace('/', '_')}"

    with mlflow.start_run(run_name=run_name) as run:
        run_id = run.info.run_id
        print(f"Starting MLflow Run (ID: {run_id}) for {model_id}...")

        # 1. Log Tags and Parameters
        mlflow.set_tag("model_type", "pretrained_transformer")
        mlflow.set_tag("source", "Hugging Face Hub")
        mlflow.set_tag("task", "emotion_detection_multilabel")
        mlflow.log_param("huggingface_model_name", model_id)

        # 2. Log Model Configuration
        print("Logging model configuration...")
        try:
            config = AutoConfig.from_pretrained(model_id)
            config_dict = config.to_dict()
            mlflow.log_params(config_dict) # Logs many config params

            # Log the crucial id2label mapping as an artifact (JSON)
            if hasattr(config, 'id2label'):
                id2label_path = "id2label_mapping.json"
                with open(id2label_path, 'w') as f:
                    json.dump(config.id2label, f, indent=4)
                mlflow.log_artifact(id2label_path, artifact_path="model_config")
                print(f"Logged id2label mapping to {id2label_path}")
            else:
                 print("Warning: id2label mapping not found in config.")

        except Exception as e:
            print(f"Could not log full config for {model_id}: {e}")

        # 3. Log a Simple "Model Info" Artifact
        # Since we aren't training, there's no model file, but we need *something*
        # to point the Model Registry entry to. A simple text file works.
        model_info_path = "model_reference.txt"
        with open(model_info_path, "w") as f:
            f.write(f"This entry represents the usage of the pre-trained Hugging Face model:\n")
            f.write(f"Model ID: {model_id}\n")
            f.write(f"MLflow Run ID: {run_id}\n")
            f.write(f"Intended Use: Multi-label Emotion Detection (GoEmotions)\n")
        mlflow.log_artifact(model_info_path, artifact_path="reference_info")
        print(f"Logged model reference to {model_info_path}")

        # 4. Register the Model in MLflow Model Registry
        print(f"Attempting to register model as '{registered_name}'...")
        try:
            # We register the run itself, or a specific artifact within it.
            # Using the reference_info artifact path is a good approach here.
            model_uri = f"runs:/{run_id}/reference_info"
            description = f"Reference to the pre-trained Hugging Face model {model_id} for multi-label emotion detection (GoEmotions)."

            mlflow.register_model(
                model_uri=model_uri,
                name=registered_name,
                tags={"source": "Hugging Face", "hf_name": model_id, "type": "emotion_detection"},
                description=description
            )
            print(f"Successfully registered model '{registered_name}' in MLflow Model Registry.")
        except Exception as e:
            print(f"Could not register model {registered_name}: {e}")
            print("This might happen if the model name already exists or due to tracking server issues.")

        # Clean up local artifact files (optional)
        if os.path.exists(id2label_path): os.remove(id2label_path)
        if os.path.exists(model_info_path): os.remove(model_info_path)

        print(f"MLflow Run (ID: {run_id}) completed.")

if __name__ == "__main__":
    log_and_register_pretrained_model(
        model_id=HF_MODEL_NAME,
        experiment_name=MLFLOW_EXPERIMENT_NAME,
        registered_name=MLFLOW_REGISTERED_MODEL_NAME
    )