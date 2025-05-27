# mental_health_ml/models/crisis/ml_crisis_predictor.py
from transformers import pipeline
import torch

# Using a multilingual zero-shot model for broader applicability initially
# In a production system, a model fine-tuned specifically on crisis data would be much preferred.
ML_CRISIS_MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

# Candidate labels for zero-shot classification
CRISIS_CANDIDATE_LABELS = [
    "expressing immediate suicidal intent or severe self-harm", # Crisis
    "expressing severe emotional distress or hopelessness",       # Potential Crisis / Concerning
    "general negative sentiment, but not a crisis",           # Non-Crisis
    "neutral or positive statement"                           # Non-Crisis
]
# We are most interested in the first one or two.

ml_crisis_pipeline = None

def load_ml_crisis_model():
    global ml_crisis_pipeline
    if ml_crisis_pipeline is None:
        try:
            print(f"Loading ML crisis model (zero-shot): {ML_CRISIS_MODEL_NAME}...")
            ml_crisis_pipeline = pipeline(
                "zero-shot-classification",
                model=ML_CRISIS_MODEL_NAME,
                device=0 if torch.cuda.is_available() else -1
            )
            print("ML crisis model (zero-shot) loaded successfully.")
        except Exception as e:
            print(f"Error loading ML crisis model {ML_CRISIS_MODEL_NAME}: {e}")
            ml_crisis_pipeline = None
    return ml_crisis_pipeline

def predict_crisis_ml(text_input: str, threshold_map: dict = None) -> dict:
    """
    Predicts crisis potential using the ML (zero-shot) model.
    Args:
        text_input (str): The user's text.
        threshold_map (dict, optional): A dictionary mapping crisis labels to confidence thresholds.
                                        e.g., {"expressing immediate suicidal intent...": 0.7}
    Returns:
        dict: {
            "ml_crisis_detected": bool,
            "ml_crisis_label": str or None (the crisis label with highest score above threshold),
            "ml_confidence": float or None,
            "all_ml_scores": dict of all candidate labels and their scores
        }
    """
    pipeline_instance = load_ml_crisis_model()
    if pipeline_instance is None:
        return {
            "ml_crisis_detected": False, "ml_crisis_label": None,
            "ml_confidence": None, "all_ml_scores": {},
            "error": "ML crisis classifier not loaded."
        }

    if threshold_map is None:
        # Default thresholds - THESE NEED CAREFUL TUNING
        threshold_map = {
            CRISIS_CANDIDATE_LABELS[0]: 0.6, # Higher threshold for immediate suicidal intent
            CRISIS_CANDIDATE_LABELS[1]: 0.5, # Slightly lower for severe distress
        }

    try:
        raw_predictions = pipeline_instance(text_input, CRISIS_CANDIDATE_LABELS, multi_label=True)
        
        all_scores = {label: 0.0 for label in CRISIS_CANDIDATE_LABELS}
        if isinstance(raw_predictions, dict) and 'labels' in raw_predictions and 'scores' in raw_predictions:
            for label, score in zip(raw_predictions['labels'], raw_predictions['scores']):
                all_scores[label] = round(score, 4)
        else: # Fallback for unexpected structure
             return {
                "ml_crisis_detected": False, "ml_crisis_label": None, "ml_confidence": None,
                "all_ml_scores": all_scores, "error": "Unexpected ML crisis prediction output"
            }


        ml_crisis_detected = False
        best_crisis_label = None
        highest_crisis_confidence = 0.0

        # Check against thresholds for crisis-indicating labels
        for label, threshold in threshold_map.items():
            if label in all_scores and all_scores[label] >= threshold:
                ml_crisis_detected = True
                # Prioritize more severe labels if multiple are above threshold
                # This logic can be made more sophisticated
                if all_scores[label] > highest_crisis_confidence: # Simple highest score wins for now
                    highest_crisis_confidence = all_scores[label]
                    best_crisis_label = label
        
        # If no crisis label met threshold, report the top overall label for context
        if not ml_crisis_detected and all_scores:
            top_label_overall = max(all_scores, key=all_scores.get)
            # If this top label is one of our defined crisis labels but just below threshold,
            # it could be a "concerning" flag. For now, we keep it simple.
            # best_crisis_label could be set to top_label_overall and highest_crisis_confidence to its score,
            # but ml_crisis_detected remains False.

        return {
            "ml_crisis_detected": ml_crisis_detected,
            "ml_crisis_label": best_crisis_label if ml_crisis_detected else None,
            "ml_confidence": highest_crisis_confidence if ml_crisis_detected else None,
            "all_ml_scores": all_scores
        }
    except Exception as e:
        print(f"Error during ML crisis prediction for text '{text_input}': {e}")
        return {
            "ml_crisis_detected": False, "ml_crisis_label": None,
            "ml_confidence": None, "all_ml_scores": {},
            "error": str(e)
        }

if __name__ == "__main__":
    load_ml_crisis_model()
    test_texts_crisis = [
        "I am planning to end my life tonight with pills.", # Should be high crisis
        "Everything feels so heavy, I don't know if I can keep going.", # Concerning, potential crisis
        "I'm just feeling really sad and down lately.", # Negative, but maybe not crisis by this model
        "I'm so angry I could scream!", # Negative, not crisis
        "Today was a good day, I felt happy.", # Positive
        "I hate everything and everyone, there's no point." # Hopelessness, potential crisis
    ]
    custom_thresholds = {
        CRISIS_CANDIDATE_LABELS[0]: 0.5, # expressing immediate suicidal intent...
        CRISIS_CANDIDATE_LABELS[1]: 0.4  # expressing severe emotional distress...
    }

    for text in test_texts_crisis:
        result = predict_crisis_ml(text, threshold_map=custom_thresholds)
        print(f"Text: \"{text}\"")
        print(f"  ML Result: {result}\n")