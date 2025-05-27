# mental_health_ml/models/assessment/nlp_zero_shot_themer.py
from transformers import pipeline
import torch # Though pipeline handles device placement, good to have if extending

# Define our target themes.
# For multilingual, it's often best if these candidate labels are in English,
# as many multilingual NLI models are trained with English hypotheses.
# The model will then see if the input text (in any supported language)
# entails these English hypotheses.
THEME_LABELS_EN = [
    "experiences sadness or hopelessness",
    "expresses anxiety or worry",
    "mentions sleep problems or insomnia",
    "reports low energy or fatigue",
    "shows loss of interest or pleasure",
    "has self-critical thoughts or guilt",
    "mentions using positive coping strategies",
    "uses language indicating a crisis or severe distress"
]
# You might also want translations if you intend to show the *detected label* to the user
# in their own language, but the classification itself often works best against English hypotheses.

# Choose the multilingual zero-shot classification model
ZERO_SHOT_MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
# This model is specifically good for cross-lingual zero-shot.
# It's based on mDeBERTa-v3-base and fine-tuned on XNLI and MNLI.

try:
    classifier_pipeline = pipeline(
        "zero-shot-classification",
        model=ZERO_SHOT_MODEL_NAME,
        device=0 if torch.cuda.is_available() else -1 # Use GPU if available
    )
    print(f"Successfully loaded multilingual zero-shot model: {ZERO_SHOT_MODEL_NAME}")
except Exception as e:
    print(f"Error loading zero-shot model {ZERO_SHOT_MODEL_NAME}: {e}")
    print("Please ensure the model name is correct, you have internet access,")
    print("and necessary dependencies (like sentencepiece for mDeBERTa) are installed.")
    classifier_pipeline = None


def predict_themes_zero_shot_multilingual(text_input: str, candidate_labels: list = None, threshold: float = 0.5) -> dict:
    """
    Predicts themes for a given text using a multilingual zero-shot classification pipeline.
    Args:
        text_input (str): The user's text (can be in various languages supported by the model).
        candidate_labels (list, optional): List of theme labels (preferably English) to classify against.
                                             Defaults to THEME_LABELS_EN.
        threshold (float, optional): Minimum score for a label to be considered "present".
                                         Defaults to 0.5.
    Returns:
        dict: A dictionary containing the input text and a list of detected themes with their scores.
    """
    if classifier_pipeline is None:
        return {"text": text_input, "detected_themes": [], "error": "Zero-shot classifier not loaded."}

    if candidate_labels is None:
        candidate_labels = THEME_LABELS_EN

    try:
        # For zero-shot, multi_label=True tells the pipeline to treat labels independently
        # and return scores for all of them that exceed some internal threshold, or scores for all if configured.
        # The output structure is {'sequence': ..., 'labels': [...], 'scores': [...]}
        # 'labels' will be from your candidate_labels.
        raw_predictions = classifier_pipeline(text_input, candidate_labels, multi_label=True)

        detected_themes = []
        if isinstance(raw_predictions, dict) and 'labels' in raw_predictions and 'scores' in raw_predictions:
            for label, score in zip(raw_predictions['labels'], raw_predictions['scores']):
                if score >= threshold:
                    detected_themes.append({"label": label, "score": round(score, 4)})
        else:
            # Handle cases where the input might be a list of texts for batching
            # or if the structure is different for some reason.
            # This simple example assumes single text input for now.
            print(f"Unexpected zero-shot output structure: {raw_predictions}")
            return {"text": text_input, "detected_themes": [], "error": "Unexpected zero-shot output structure"}

        # Sort by score descending for better presentation
        detected_themes = sorted(detected_themes, key=lambda x: x['score'], reverse=True)

        return {
            "text": text_input,
            "detected_themes": detected_themes,
            "model_version_tag": f"zero_shot_{ZERO_SHOT_MODEL_NAME.replace('/', '_')}" # Make filename friendly
        }
    except Exception as e:
        print(f"Error during multilingual zero-shot prediction for text '{text_input}': {e}")
        return {"text": text_input, "detected_themes": [], "error": str(e)}

if __name__ == "__main__":
    # Example Usage
    sample_texts = [
        # English
        "I've been feeling really down and can't seem to enjoy anything anymore. Sleep is a mess too.",
        "I'm so worried about my exams, I can barely focus.",
        "Today I went for a walk and talked to a friend, it helped a bit.",
        # Spanish
        "Me siento muy triste últimamente y no duermo bien.", # "I feel very sad lately and I don't sleep well."
        "Estoy intentando nuevas formas de manejar mi estrés.", # "I am trying new ways to manage my stress."
        # French
        "Je n'ai plus goût à rien et je suis fatigué en permanence.", # "I have no taste for anything anymore and I am permanently tired."
        "Je suis préoccupé par mon avenir.", # "I am worried about my future."
        # A neutral or less emotional statement
        "The weather is nice today."
    ]

    # Using a slightly lower threshold for zero-shot as scores might not always be extremely high
    # This threshold should be tuned based on evaluation.
    detection_threshold = 0.3

    for text in sample_texts:
        print(f"\n--- Analyzing: '{text}' ---")
        themes_result = predict_themes_zero_shot_multilingual(text, threshold=detection_threshold)
        if "error" in themes_result and themes_result["error"]:
            print(f"Error: {themes_result['error']}")
        elif not themes_result["detected_themes"]:
            print("No themes detected above threshold.")
        else:
            print("Detected Themes:")
            for theme in themes_result["detected_themes"]:
                print(f"  - {theme['label']}: {theme['score']:.4f}")
        print(f"Model: {themes_result.get('model_version_tag', 'N/A')}")