# mental_health_ml/training/register_assessment_scorers.py
import mlflow
import os
import json
from dotenv import load_dotenv

from mental_health_ml.models.assessment.scoring_rules import (
    PHQ9_QUESTIONNAIRE_NAME, PHQ9_SEVERITY_CATEGORIES,
    GAD7_QUESTIONNAIRE_NAME, GAD7_SEVERITY_CATEGORIES
)

load_dotenv()

def end_any_active_run():
    """Checks if an MLflow run is active and ends it."""
    if mlflow.active_run():
        print(f"Ending an existing active run: {mlflow.active_run().info.run_id}")
        mlflow.end_run()

def register_scorer_rules(experiment_name: str, model_name: str, rules: dict, questionnaire_name: str, run_description: str): # Changed param name for clarity
    end_any_active_run()

    mlflow.set_experiment(experiment_name)
    run_name = f"{model_name}_rules_registration"

    with mlflow.start_run(run_name=run_name) as run:
        # Set the run description using a tag (MLflow standard practice)
        mlflow.set_tag("mlflow.note.content", run_description) # Or just "description" if you prefer
        mlflow.set_tag("model_type", "rule_based_scorer")
        mlflow.set_tag("questionnaire", questionnaire_name)

        rules_for_mlflow_param = {str(k): v for k, v in rules.items()}
        mlflow.log_param(f"{questionnaire_name}_severity_categories", json.dumps(rules_for_mlflow_param))

        print(f"Run ID for {model_name}: {run.info.run_id}")
        print(f"Experiment ID: {run.info.experiment_id}")

        rules_for_artifact = {str(k): v for k, v in rules.items()}
        # Log the dictionary as a JSON artifact
        artifact_file_name = f"{questionnaire_name}_rules.json"
        mlflow.log_dict(rules_for_artifact, artifact_file_name)
        print(f"Logged artifact: {artifact_file_name}")


        try:
            # --- MODIFICATION START ---
            # Removed the 'description' argument from register_model
            mlflow.register_model(
                model_uri=f"runs:/{run.info.run_id}/{artifact_file_name}", # Use the logged artifact
                name=model_name,
                tags={"questionnaire": questionnaire_name, "type": "rule_based"}
            )
            # --- MODIFICATION END ---
            print(f"Registered model version for '{model_name}' ({questionnaire_name})")
        except Exception as e:
            print(f"Could not register model {model_name} (or new version): {e}. This might happen if the model with this name already exists and you are trying to create it again. New versions should be created automatically if the name matches.")


if __name__ == "__main__":
    assessment_experiment_name = "MentalHealthAssessmentScorers"

    print(f"Using MLflow tracking URI: {mlflow.get_tracking_uri()}")
    end_any_active_run()

    register_scorer_rules(
        experiment_name=assessment_experiment_name,
        model_name="PHQ9_Scorer_Rules", # Using a general name, versions will be created under this
        rules=PHQ9_SEVERITY_CATEGORIES,
        questionnaire_name=PHQ9_QUESTIONNAIRE_NAME,
        run_description="Initial rule set for PHQ-9 standard scoring." # This description is for the run
    )

    register_scorer_rules(
        experiment_name=assessment_experiment_name,
        model_name="GAD7_Scorer_Rules", # Using a general name
        rules=GAD7_SEVERITY_CATEGORIES,
        questionnaire_name=GAD7_QUESTIONNAIRE_NAME,
        run_description="Initial rule set for GAD-7 standard scoring." # This description is for the run
    )
    print("Rule-based scorer parameters and rule artifacts logged to MLflow.")