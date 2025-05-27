# mental_health_ml/tests/unit/test_hybrid_crisis_detector.py
import pytest
from unittest.mock import patch
# Assuming your hybrid detector is in this path
from mental_health_ml.models.crisis.hybrid_crisis_detector import detect_crisis_hybrid, load_ml_crisis_model
# To access CRISIS_CANDIDATE_LABELS for mocking ML output
from mental_health_ml.models.crisis.ml_crisis_predictor import CRISIS_CANDIDATE_LABELS as ML_CRISIS_LABELS


@pytest.fixture(scope="module", autouse=True)
def load_models_for_test():
    # This ensures the ML model (pipeline) is loaded once before tests run.
    # In a real CI, this might download the model if not cached.
    print("Pre-loading ML crisis model for hybrid detector tests...")
    load_ml_crisis_model()
    print("ML crisis model pre-loaded.")

def test_keyword_triggers_crisis():
    text = "I want to kill myself."
    result = detect_crisis_hybrid(text)
    assert result["is_crisis"] is True
    assert "keyword_suicide_intent_explicit" in result["crisis_type"]
    assert result["confidence"] > 0.9 # Keyword confidence

def test_ml_triggers_crisis_no_keyword():
    text = "Everything is just too much, I feel completely overwhelmed and heavy."
    # Mock the output of predict_crisis_ml to simulate an ML detection
    mock_ml_output = {
        "ml_crisis_detected": True,
        "ml_crisis_label": ML_CRISIS_LABELS[1], # "expressing severe emotional distress..."
        "ml_confidence": 0.75,
        "all_ml_scores": {ML_CRISIS_LABELS[1]: 0.75, ML_CRISIS_LABELS[0]: 0.2}
    }
    with patch('mental_health_ml.models.crisis.hybrid_crisis_detector.predict_crisis_ml', return_value=mock_ml_output):
        result = detect_crisis_hybrid(text)
        assert result["is_crisis"] is True
        assert "ml_severe_distress_ml" in result["crisis_type"] # Check for sanitized label
        assert result["confidence"] == 0.75

def test_no_crisis_detected():
    text = "I'm having a pretty good day."
    mock_ml_output = { # ML also sees no crisis
        "ml_crisis_detected": False,
        "ml_crisis_label": None,
        "ml_confidence": None,
        "all_ml_scores": {ML_CRISIS_LABELS[3]: 0.8, ML_CRISIS_LABELS[2]: 0.1} # "neutral or positive"
    }
    with patch('mental_health_ml.models.crisis.hybrid_crisis_detector.predict_crisis_ml', return_value=mock_ml_output):
        result = detect_crisis_hybrid(text)
        assert result["is_crisis"] is False
        assert result["crisis_type"] is None

def test_keyword_overrides_ml_non_crisis():
    text = "I want to die but the weather is nice." # Keyword present
    # Even if ML thought it wasn't a crisis (which it shouldn't for this text)
    mock_ml_output = {
        "ml_crisis_detected": False, "ml_crisis_label": None, "ml_confidence": None,
        "all_ml_scores": {ML_CRISIS_LABELS[3]: 0.6}
    }
    # The patch won't even be strictly necessary for this test case if keywords are checked first
    # but good to show how one might control ML output if needed.
    with patch('mental_health_ml.models.crisis.hybrid_crisis_detector.predict_crisis_ml', return_value=mock_ml_output):
        result = detect_crisis_hybrid(text)
        assert result["is_crisis"] is True
        assert "keyword" in result["crisis_type"] # Keyword system should catch it

# Add tests for different threshold_map inputs to ml_crisis_predictor via detect_crisis_hybrid