# mental_health_ml/models/emotion/emotion_predictor.py
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Using the GoEmotions model
EMOTION_MODEL_NAME = "SamLowe/roberta-base-go_emotions"

# Global variable to hold the pipeline and model labels
emotion_classifier_pipeline = None
model_id2label = {} # To store the mapping from index to label name
model_label2id = {} # To store the mapping from label name to index

def load_emotion_model():
    """Loads the GoEmotions classification pipeline and its label mapping."""
    global emotion_classifier_pipeline, model_id2label, model_label2id
    if emotion_classifier_pipeline is None:
        try:
            print(f"Loading emotion model: {EMOTION_MODEL_NAME}...")
            # We need the model and tokenizer separately to easily access config for labels
            # The pipeline will use these.
            tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(EMOTION_MODEL_NAME)

            # The pipeline will handle tokenization and model prediction
            emotion_classifier_pipeline = pipeline(
                "text-classification",
                model=model, # Pass the loaded model
                tokenizer=tokenizer, # Pass the loaded tokenizer
                return_all_scores=True, # Crucial for getting scores for all 28 labels
                device=0 if torch.cuda.is_available() else -1
            )

            # Get the model's config to extract labels
            # GoEmotions models typically have id2label and label2id in their config
            if hasattr(model.config, 'id2label'):
                model_id2label = model.config.id2label
                model_label2id = model.config.label2id # Also useful
                print(f"Emotion model loaded successfully. {len(model_id2label)} labels detected (e.g., 0: {model_id2label.get(0)}, 1: {model_id2label.get(1)}).")
            else:
                print(f"Warning: Could not reliably get id2label from model config for {EMOTION_MODEL_NAME}.")
                print("This might affect mapping scores to specific emotion names if pipeline output is not clear.")
                # If this happens, you might need to manually define the labels based on the GoEmotions paper/dataset.
                # The GoEmotions labels are: admiration, amusement, anger, annoyance, approval, caring, confusion,
                # curiosity, desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, gratitude,
                # grief, joy, love, nervousness, optimism, pride, realization, relief, remorse, sadness, surprise, neutral

        except Exception as e:
            print(f"Error loading emotion model {EMOTION_MODEL_NAME}: {e}")
            emotion_classifier_pipeline = None
    return emotion_classifier_pipeline

def predict_emotion_goemotions(text_input: str, threshold: float = 0.1) -> dict:
    """
    Predicts emotions for a given text using the GoEmotions model.
    This model is multi-label, so multiple emotions can be predicted for a single text.

    Args:
        text_input (str): The user's text (primarily English for this model).
        threshold (float): Minimum score for an emotion to be included in 'active_emotions'.
                           Adjust based on desired sensitivity. GoEmotions scores can be widespread.

    Returns:
        dict: A dictionary containing:
              - 'text': the input text
              - 'active_emotions': list of emotions with scores above the threshold
              - 'all_emotion_scores': a dict of all 28 emotions and their scores
              - 'model_version_tag': identifier for the model used
              - 'error': error message if prediction fails
    """
    pipeline_instance = load_emotion_model()
    if pipeline_instance is None or not model_id2label: # Ensure labels are loaded too
        return {
            "text": text_input,
            "active_emotions": [],
            "all_emotion_scores": {},
            "error": "GoEmotions classifier or label mapping not loaded properly."
        }

    try:
        # Pipeline with return_all_scores=True for this model returns a list of lists of dicts.
        # For a single input string, it's typically [[{'label': 'LABEL_0', 'score': ...}, {'label': 'LABEL_1', ...}]]
        # The 'label' here will be like 'LABEL_0', 'LABEL_1', etc., up to 'LABEL_27'.
        # We need to map these back to actual emotion names using model_id2label.
        raw_predictions_wrapper = pipeline_instance(text_input)

        if not raw_predictions_wrapper or not isinstance(raw_predictions_wrapper, list) or \
           not isinstance(raw_predictions_wrapper[0], list):
            raise ValueError(f"Unexpected output format from pipeline: {raw_predictions_wrapper}")

        raw_predictions = raw_predictions_wrapper[0] # Get the list of score dicts

        all_emotion_scores = {}
        active_emotions = []

        for item in raw_predictions:
            label_index_str = item['label'].replace('LABEL_', '') # Extract index from 'LABEL_X'
            try:
                label_index = int(label_index_str)
                emotion_name = model_id2label.get(label_index, f"unknown_label_{label_index}")
                score = round(item['score'], 4)
                all_emotion_scores[emotion_name] = score
                if score >= threshold:
                    active_emotions.append({"emotion": emotion_name, "score": score})
            except ValueError:
                print(f"Warning: Could not parse label index from '{item['label']}'")
                continue # Skip this problematic label

        # Sort active emotions by score for clarity
        active_emotions = sorted(active_emotions, key=lambda x: x['score'], reverse=True)

        # Find the single "dominant" emotion if needed for a simpler output, though multi-label is the strength here
        dominant_emotion = active_emotions[0]['emotion'] if active_emotions else "neutral" # Default to neutral if no active emotions
        dominant_emotion_score = active_emotions[0]['score'] if active_emotions else all_emotion_scores.get("neutral", 0.0)


        return {
            "text": text_input,
            "dominant_emotion": dominant_emotion, # Optional: single top emotion
            "dominant_emotion_score": dominant_emotion_score, # Optional
            "active_emotions": active_emotions, # Emotions above threshold
            "all_emotion_scores": all_emotion_scores, # Scores for all 28 classes
            "model_version_tag": f"pretrained_{EMOTION_MODEL_NAME.replace('/', '_')}"
        }
    except Exception as e:
        print(f"Error during GoEmotions prediction for text '{text_input}': {e}")
        return {
            "text": text_input,
            "active_emotions": [],
            "all_emotion_scores": {},
            "error": str(e)
        }

if __name__ == "__main__":
    # Ensure model loads on first call
    load_emotion_model()
    if emotion_classifier_pipeline: # Proceed only if model loaded
        sample_texts = [
            "I am so happy and excited about this! This is amazing news.",
            "This is really frustrating and makes me angry. I'm quite annoyed.",
            "I feel very sad and lonely today. I miss my friend.",
            "Wow, that's a big surprise! I wasn't expecting that at all.",
            "I'm scared of what might happen next, feeling very nervous.",
            "The meeting is scheduled for 3 PM tomorrow.", # Should be neutral
            "Thank you so much for your help, I really appreciate it!", # Gratitude, Joy
            "I'm a bit confused about these instructions.", # Confusion
            "I wish I could go on a vacation right now.", # Desire
            "I'm so proud of my team's achievement!" # Pride, Joy
        ]

        # GoEmotions scores can be spread out, a lower threshold might be needed to see multiple active emotions
        # This threshold needs tuning based on experimentation and desired output.
        detection_threshold = 0.05 # Example: show emotions with at least 5% score

        for text in sample_texts:
            print(f"\n--- Analyzing: '{text}' ---")
            emotion_result = predict_emotion_goemotions(text, threshold=detection_threshold)
            if "error" in emotion_result and emotion_result["error"]:
                print(f"  Error: {emotion_result['error']}")
            else:
                print(f"  Dominant Emotion: {emotion_result.get('dominant_emotion', 'N/A')} (Score: {emotion_result.get('dominant_emotion_score', 'N/A'):.4f})")
                print(f"  Active Emotions (score >= {detection_threshold}):")
                if emotion_result["active_emotions"]:
                    for em in emotion_result["active_emotions"]:
                        print(f"    - {em['emotion']}: {em['score']:.4f}")
                else:
                    print("    (None above threshold)")
                # print(f"  All Scores: {emotion_result['all_emotion_scores']}") # Uncomment to see all 28 scores
                print(f"  Model: {emotion_result.get('model_version_tag', 'N/A')}")
    else:
        print("Emotion model pipeline could not be loaded. Skipping examples.")