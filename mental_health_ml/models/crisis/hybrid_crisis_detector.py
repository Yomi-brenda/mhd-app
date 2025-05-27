# mental_health_ml/models/crisis/hybrid_crisis_detector.py
from .keyword_crisis_detector import detect_crisis_keywords
from .ml_crisis_predictor import predict_crisis_ml, load_ml_crisis_model # Ensure model loads

# Confidence score for keyword detection can be considered very high
KEYWORD_CRISIS_CONFIDENCE = 0.99

def detect_crisis_hybrid(text_input: str, ml_threshold_map: dict = None) -> dict:
    """
    Combines keyword and ML-based crisis detection.
    Args:
        text_input (str): The user's text.
        ml_threshold_map (dict, optional): Thresholds for ML crisis predictor.
    Returns:
        dict: {
            "is_crisis": bool,
            "confidence": float,
            "crisis_type": str (e.g., "keyword_suicide_intent", "ml_suicidal_intent_expression"),
            "details": {
                "keyword_result": dict from detect_crisis_keywords,
                "ml_result": dict from predict_crisis_ml
            }
        }
    """
    # Ensure ML model is loaded if it hasn't been already
    load_ml_crisis_model()

    keyword_result = detect_crisis_keywords(text_input)
    
    # Layer 1: Keyword detection takes precedence for immediate flagging
    if keyword_result["keyword_crisis_detected"]:
        return {
            "is_crisis": True,
            "confidence": KEYWORD_CRISIS_CONFIDENCE, # Assign high confidence
            "crisis_type": f"keyword_{keyword_result['matched_category']}",
            "triggering_text_segment": keyword_result.get('matched_pattern'), # The regex pattern
            "details": {"keyword_result": keyword_result, "ml_result": None}
        }

    # Layer 2: ML-based detection if no keywords matched
    ml_result = predict_crisis_ml(text_input, threshold_map=ml_threshold_map)
    
    if ml_result.get("error"): # Handle potential error from ML predictor
        print(f"Warning: ML crisis prediction failed: {ml_result['error']}")
        # Fallback: no crisis detected by ML if it errored. Consider logging this.
        is_ml_crisis = False
        ml_confidence = 0.0
        ml_crisis_type = None
    else:
        is_ml_crisis = ml_result["ml_crisis_detected"]
        ml_confidence = ml_result.get("ml_confidence", 0.0) if is_ml_crisis else 0.0
        ml_crisis_type = f"ml_{ml_result.get('ml_crisis_label', 'unknown')}" if is_ml_crisis else None
        # Sanitize label for crisis_type if needed
        if ml_crisis_type:
            ml_crisis_type = ml_crisis_type.replace("expressing immediate suicidal intent or severe self-harm", "suicidal_intent_ml") \
                                        .replace("expressing severe emotional distress or hopelessness", "severe_distress_ml") \
                                        .replace(" ", "_").lower()


    if is_ml_crisis:
        return {
            "is_crisis": True,
            "confidence": ml_confidence,
            "crisis_type": ml_crisis_type,
            "triggering_text_segment": text_input, # For ML, the whole text is usually the trigger
            "details": {"keyword_result": keyword_result, "ml_result": ml_result}
        }

    # No crisis detected by either layer
    return {
        "is_crisis": False,
        "confidence": 1.0 - max(keyword_result.get("keyword_crisis_detected",0), ml_result.get("all_ml_scores", {}).get(CRISIS_CANDIDATE_LABELS[0], 0)), # Confidence it's NOT crisis
        "crisis_type": None,
        "triggering_text_segment": None,
        "details": {"keyword_result": keyword_result, "ml_result": ml_result}
    }

if __name__ == "__main__":
    # Ensure models are loaded (especially the ML one for its first use)
    print("Initializing crisis detection systems...")
    load_ml_crisis_model() # Important to call to load the pipeline
    print("Initialization complete.")

    test_texts_hybrid = [
        "I want to kill myself tonight.", # Keyword
        "Life is pointless and I don't want to be here anymore.", # Keyword (hopelessness) and ML
        "I'm thinking about ways to overdose because I can't handle the pain.", # Keyword + ML
        "I feel extremely anxious and panicky, like the world is ending.", # ML (severe distress)
        "I'm just sad today.", # ML (should be non-crisis by ML or low score)
        "Everything is great!", # Non-crisis
        "I'm not going to hurt myself, don't worry.", # Keyword might catch, ML should ideally say non-crisis
    ]
    # Define thresholds for the ML layer (these are examples, TUNE CAREFULLY)
    # from .ml_crisis_predictor import CRISIS_CANDIDATE_LABELS # To access labels easily
    # For testing, use the labels as defined in ml_crisis_predictor
    # This is a bit of a circular dependency for __main__, better to define them once globally or pass.
    # For this example, let's assume CRISIS_CANDIDATE_LABELS from ml_crisis_predictor is accessible or redefined here.
    _CRISIS_CANDIDATE_LABELS_TEST = [
        "expressing immediate suicidal intent or severe self-harm",
        "expressing severe emotional distress or hopelessness",
        "general negative sentiment, but not a crisis",
        "neutral or positive statement"
    ]
    custom_ml_thresholds = {
        _CRISIS_CANDIDATE_LABELS_TEST[0]: 0.5, # suicidal intent
        _CRISIS_CANDIDATE_LABELS_TEST[1]: 0.4  # severe distress
    }


    for text in test_texts_hybrid:
        result = detect_crisis_hybrid(text, ml_threshold_map=custom_ml_thresholds)
        print(f"Text: \"{text}\"")
        print(f"  Hybrid Result: Is Crisis? {result['is_crisis']}, Type: {result['crisis_type']}, Conf: {result.get('confidence', 'N/A'):.2f}")
        # print(f"  Details: {result['details']}\n") # Uncomment for full details
        if result['is_crisis']:
             print(f"  TRIGGER: {result.get('triggering_text_segment', 'N/A')}")
        print("-" * 20)