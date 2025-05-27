# mental_health_ml/models/emotion/predictor.py
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict, Optional, Union

# Define the model identifier from Hugging Face Hub
MODEL_NAME = "SamLowe/roberta-base-go_emotions"
MODEL_VERSION_TAG = "SamLowe-roberta-base-go_emotions-v1" # Custom tag for our use

_emotion_classifier_pipeline = None

def _load_model():
    """Loads the model and tokenizer pipeline if they haven't been loaded yet."""
    global _emotion_classifier_pipeline
    if _emotion_classifier_pipeline is None:
        print(f"Loading emotion detection model: {MODEL_NAME}...")
        # This model is multi-label, so the pipeline will output scores for all labels.
        # We'll apply a threshold later.
        _emotion_classifier_pipeline = pipeline(
            "text-classification",
            model=MODEL_NAME,
            tokenizer=MODEL_NAME,
            return_all_scores=True # Ensures we get scores for all 28 labels
        )
        print("Emotion detection model loaded.")
    return _emotion_classifier_pipeline

def predict_emotions_multi_label(text: str, threshold: float = 0.3) -> Optional[Dict[str, Union[List[str], Dict[str, float], str]]]:
    """
    Predicts multiple emotions from a given text using 'SamLowe/roberta-base-go_emotions'.

    Args:
        text (str): The input text to analyze.
        threshold (float): Confidence threshold to consider an emotion as "present".

    Returns:
        Optional[Dict[str, Union[List[str], Dict[str, float], str]]]]:
        A dictionary containing:
            - 'detected_emotions': A list of emotions exceeding the threshold.
            - 'confidence_scores': A dictionary of all emotions and their raw scores.
            - 'model_version_tag': The version tag of the model used.
        Returns None if an error occurs.
    """
    if not text or not isinstance(text, str):
        return {
            "detected_emotions": ["error"],
            "confidence_scores": {"error": "Input text must be a non-empty string."},
            "model_version_tag": MODEL_VERSION_TAG
        }

    try:
        classifier = _load_model()
        # The pipeline with return_all_scores=True for a single string input
        # returns a list containing one list of dictionaries:
        # e.g., [[{'label': 'admiration', 'score': 0.95}, {'label': 'amusement', 'score': 0.02}, ...]]
        raw_predictions = classifier(text)

        if not raw_predictions or not raw_predictions[0]:
            return {
                "detected_emotions": ["error"],
                "confidence_scores": {"error": "Model did not return valid predictions."},
                "model_version_tag": MODEL_VERSION_TAG
            }

        all_scores_dict = {p['label']: p['score'] for p in raw_predictions[0]}
        
        detected_emotions_list = [
            label for label, score in all_scores_dict.items() if score > threshold
        ]

        # If no emotion exceeds threshold, but neutral is high, consider it neutral.
        # Or, if 'neutral' is the highest and nothing else passes threshold.
        if not detected_emotions_list and all_scores_dict.get('neutral', 0) > threshold / 2 : # Heuristic
             # Check if neutral is among the highest scores even if it doesn't pass strict threshold alone
            sorted_emotions = sorted(all_scores_dict.items(), key=lambda item: item[1], reverse=True)
            if sorted_emotions and sorted_emotions[0][0] == 'neutral':
                 detected_emotions_list = ['neutral']

        # If still no emotions detected (e.g. all scores are very low), default to neutral or unknown
        if not detected_emotions_list:
            if 'neutral' in all_scores_dict: # Check if 'neutral' is a label
                detected_emotions_list = ['neutral'] # Default to neutral if available
            else:
                detected_emotions_list = ['unknown']


        return {
            "detected_emotions": detected_emotions_list,
            "confidence_scores": all_scores_dict,
            "model_version_tag": MODEL_VERSION_TAG
        }

    except Exception as e:
        print(f"Error during emotion prediction: {e}")
        # In a real app, log this exception properly
        return {
            "detected_emotions": ["error"],
            "confidence_scores": {"error": str(e)},
            "model_version_tag": MODEL_VERSION_TAG
        }

if __name__ == "__main__":
    _load_model() # Pre-load

    sample_texts = [
        "This is amazing! I'm so happy and excited about this news.", # joy, excitement, (admiration?)
        "I feel a bit sad and also a little worried about the future.", # sadness, nervousness (fear?)
        "That's hilarious, I can't stop laughing but I'm also surprised.", # amusement, surprise
        "Just a regular Tuesday morning.", # neutral
        "I am utterly disappointed and quite angry.", # disappointment, anger
        "What a relief, I was so scared!", # relief, fear
        "This book is quite interesting." # curiosity, interest (or neutral)
    ]

    custom_threshold = 0.3 # You might need to tune this threshold

    for sample_text in sample_texts:
        result = predict_emotions_multi_label(sample_text, threshold=custom_threshold)
        print(f"\nText: \"{sample_text}\"")
        if result:
            print(f"  Detected Emotions (>{custom_threshold}): {result['detected_emotions']}")
            # print(f"  All Scores: {result['confidence_scores']}") # Can be very verbose
            top_3_scores = sorted(result['confidence_scores'].items(), key=lambda item: item[1], reverse=True)[:3]
            print(f"  Top 3 scores: { {label: round(score, 3) for label, score in top_3_scores} }")
            print(f"  Model: {result['model_version_tag']}")
        else:
            print("  Failed to get emotion prediction.")