# mental_health_ml/training/register_crisis_detection_system.py
import mlflow
import os
import json
from dotenv import load_dotenv

# Import model names or identifiers if they are defined centrally
from mental_health_ml.models.crisis.keyword_crisis_detector import (
    SUICIDE_INTENT_PATTERNS, HOPELESSNESS_PATTERNS, SELF_HARM_PATTERNS
)
from mental_health_ml.models.crisis.ml_crisis_predictor import ML_CRISIS_MODEL_NAME

load_dotenv()

MLFLOW_EXPERIMENT_NAME = "Crisis_Detection_Systems"
REGISTERED_MODEL_NAME = "HybridCrisisDetector" # Name for our combined system

if __name__ == "__main__":
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    run_name = f"Log_Hybrid_Crisis_Detector_v1.0" # Increment version as system evolves

    with mlflow.start_run(run_name=run_name) as run:
        print(f"MLflow Run ID: {run.info.run_id} for Hybrid Crisis Detector")

        mlflow.set_tag("system_type", "hybrid_keyword_ml")
        mlflow.set_tag("layer1_type", "keyword_regex")
        mlflow.set_tag("layer2_type", "zero_shot_transformer")

        # Log parameters for Layer 1 (Keywords)
        # Storing lists of regex patterns as params can be verbose; consider logging as artifact
        keyword_config = {
            "suicide_intent_patterns_count": len(SUICIDE_INTENT_PATTERNS),
            "hopelessness_patterns_count": len(HOPELESSNESS_PATTERNS),
            "self_harm_patterns_count": len(SELF_HARM_PATTERNS)
        }
        mlflow.log_params(keyword_config)
        # Log the actual patterns as a JSON artifact
        all_keyword_patterns = {
            "suicide": SUICIDE_INTENT_PATTERNS,
            "hopelessness": HOPELESSNESS_PATTERNS,
            "self_harm": SELF_HARM_PATTERNS
        }
        mlflow.log_dict(all_keyword_patterns, "keyword_patterns.json")


        # Log parameters for Layer 2 (ML Model)
        mlflow.log_param("ml_model_huggingface_name", ML_CRISIS_MODEL_NAME)
        # Log default thresholds used if any, or note they are passed at runtime
        # For example, from ml_crisis_predictor.py if we had defaults:
        # default_ml_thresholds = {CRISIS_CANDIDATE_LABELS[0]: 0.6, ...}
        # mlflow.log_param("ml_default_thresholds", json.dumps(default_ml_thresholds))


        # Log evaluation metrics IF you have a benchmark dataset and evaluation script
        # This would involve running detect_crisis_hybrid on a labeled test set
        # For now, we'll skip this as we haven't defined that evaluation process yet.
        # Example:
        # test_results = evaluate_crisis_detector(test_data_path="...")
        # mlflow.log_metrics({
        #     "overall_recall_crisis": test_results["recall_crisis"],
        #     "overall_precision_crisis": test_results["precision_crisis"],
        #     "overall_f1_crisis": test_results["f1_crisis"]
        # })

        # Log a "model info" artifact for the hybrid system
        system_info_path = "hybrid_crisis_system_info.txt"
        with open(system_info_path, "w") as f:
            f.write(f"Hybrid Crisis Detection System v1.0\n")
            f.write(f"Layer 1: Keywords (see keyword_patterns.json artifact)\n")
            f.write(f"Layer 2: ML Model - {ML_CRISIS_MODEL_NAME}\n")
        mlflow.log_artifact(system_info_path, artifact_path="system_details")

        try:
            mlflow.register_model(
                model_uri=f"runs:/{run.info.run_id}/system_details",
                name=REGISTERED_MODEL_NAME,
                tags={"type": "hybrid_crisis_detection"},
                description="Hybrid system combining keywords and ML for crisis detection."
            )
            print(f"Registered '{REGISTERED_MODEL_NAME}' in MLflow Model Registry.")
        except Exception as e:
            print(f"Could not register model {REGISTERED_MODEL_NAME}: {e}")
        
        if os.path.exists(system_info_path): os.remove(system_info_path)