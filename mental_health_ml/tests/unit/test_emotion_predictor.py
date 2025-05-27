# # mental_health_ml/tests/unit/test_emotion_predictor.py
# import pytest
# from mental_health_ml.models.emotion.predictor import predict_emotions_multi_label, _load_model, MODEL_VERSION_TAG

# @pytest.fixture(scope="module", autouse=True)
# def load_model_once():
#     _load_model()

# # The GoEmotions model has 27 specific emotions + neutral.
# # We'll test for presence of expected emotions, not exclusive dominance.
# # Example labels from GoEmotions: admiration, amusement, anger, annoyance, approval, caring,
# # confusion, curiosity, desire, disappointment, disapproval, disgust, embarrassment,
# # excitement, fear, gratitude, grief, joy, love, nervousness, optimism, pride,
# # realization, relief, remorse, sadness, surprise, neutral.

# def test_predict_joy_excitement(self):
#     text = "This is fantastic news, I'm thrilled and so happy!"
#     # For GoEmotions, we might expect 'joy', 'excitement', 'optimism', 'admiration' etc.
#     result = predict_emotions_multi_label(text, threshold=0.2) # Use a threshold for testing
#     assert result is not None
#     assert "joy" in result["detected_emotions"]
#     assert "excitement" in result["detected_emotions"]
#     assert result["model_version_tag"] == MODEL_VERSION_TAG
#     assert isinstance(result["confidence_scores"], dict)
#     assert result["confidence_scores"]["joy"] > 0.1 # Check if score is reasonably high

# def test_predict_sadness_grief(self):
#     text = "I'm heartbroken and feeling deep sorrow."
#     result = predict_emotions_multi_label(text, threshold=0.2)
#     assert result is not None
#     assert "sadness" in result["detected_emotions"]
#     assert "grief" in result["detected_emotions"] # GoEmotions has 'grief'
#     assert result["confidence_scores"]["sadness"] > 0.1

# def test_predict_anger_annoyance(self):
#     text = "This is infuriating! I'm so annoyed by their actions."
#     result = predict_emotions_multi_label(text, threshold=0.2)
#     assert result is not None
#     assert "anger" in result["detected_emotions"]
#     assert "annoyance" in result["detected_emotions"]
#     assert result["confidence_scores"]["anger"] > 0.1

# def test_neutral_text(self):
#     text = "The report is due by 5 PM."
#     result = predict_emotions_multi_label(text, threshold=0.3) # Higher threshold for neutral check
#     assert result is not None
#     # Check if 'neutral' is the primary or only one if others are low
#     if len(result["detected_emotions"]) == 1:
#         assert "neutral" in result["detected_emotions"]
#     elif "neutral" in result["detected_emotions"]:
#          assert result["confidence_scores"]["neutral"] > 0.1 # Should be relatively high
#     # This test is harder to make robust for multi-label without knowing exact score distribution

# def test_empty_input(self):
#     text = ""
#     result = predict_emotions_multi_label(text)
#     assert result is not None
#     assert "error" in result["detected_emotions"]
#     assert "error" in result["confidence_scores"]

# def test_output_structure_multi_label(self):
#     text = "Just a test."
#     result = predict_emotions_multi_label(text)
#     assert result is not None
#     assert "detected_emotions" in result
#     assert "confidence_scores" in result
#     assert "model_version_tag" in result
#     assert isinstance(result["detected_emotions"], list)
#     assert isinstance(result["confidence_scores"], dict)
#     assert isinstance(result["model_version_tag"], str)
#     # Check if all expected GoEmotions labels are keys in confidence_scores
#     # This is a long list (28 labels) - for brevity, check a few
#     go_emotion_sample_labels = {"admiration", "anger", "sadness", "joy", "neutral", "fear", "surprise"}
#     assert go_emotion_sample_labels.issubset(result["confidence_scores"].keys())

# # It's important to understand that for multi-label, asserting exact detected_emotions lists
# # can be brittle. Focus on presence of key expected emotions and sensible scores.
# # The threshold value in tests might need adjustment based on observed model behavior.

# mental_health_ml/tests/unit/test_emotion_predictor.py
import pytest
from mental_health_ml.models.emotion.emotion_predictor import predict_emotion_goemotions, load_emotion_model, EMOTION_MODEL_NAME

# Fixture to ensure model is loaded once for tests
@pytest.fixture(scope="module", autouse=True)
def model_loader():
    print(f"Loading emotion model ({EMOTION_MODEL_NAME}) for tests...")
    loaded_pipeline = load_emotion_model()
    if loaded_pipeline is None:
        pytest.fail(f"Failed to load GoEmotions model {EMOTION_MODEL_NAME} for testing.")
    print("GoEmotions model loaded for tests.")

def test_predict_multiple_emotions_positive():
    text = "This is amazing news! I'm so happy and excited, and very grateful!"
    # Use a threshold that's likely to pick up multiple distinct emotions
    result = predict_emotion_goemotions(text, threshold=0.05)

    assert "error" not in result or result["error"] is None
    assert isinstance(result["active_emotions"], list)
    assert isinstance(result["all_emotion_scores"], dict)
    assert len(result["all_emotion_scores"]) >= 28 # Should have scores for all GoEmotions labels

    active_emotion_names = [em["emotion"] for em in result["active_emotions"]]
    print(f"Positive Text Active Emotions: {active_emotion_names} with scores: {result['active_emotions']}")

    # Expect some positive emotions to be present with reasonable scores
    # Exact top emotion can vary, focus on presence of expected ones
    assert any(em in active_emotion_names for em in ["joy", "excitement", "gratitude", "admiration"])
    assert "sadness" not in active_emotion_names or result["all_emotion_scores"].get("sadness", 0) < 0.1 # sadness score should be low

def test_predict_multiple_emotions_negative():
    text = "I'm really disappointed and angry about this. It makes me sad too."
    result = predict_emotion_goemotions(text, threshold=0.05)

    assert "error" not in result or result["error"] is None
    active_emotion_names = [em["emotion"] for em in result["active_emotions"]]
    print(f"Negative Text Active Emotions: {active_emotion_names} with scores: {result['active_emotions']}")

    assert any(em in active_emotion_names for em in ["disappointment", "anger", "sadness", "annoyance"])
    assert "joy" not in active_emotion_names or result["all_emotion_scores"].get("joy", 0) < 0.1 # joy score should be low

def test_predict_neutral_text():
    text = "The document is on the shared drive."
    result = predict_emotion_goemotions(text, threshold=0.1) # Higher threshold for neutral
    # For truly neutral text, 'neutral' should ideally be high, or all other scores low.
    # The "dominant_emotion" defaulting to neutral if no active emotions is one way to handle it.

    print(f"Neutral Text Result: {result}")
    assert "error" not in result or result["error"] is None

    if result["active_emotions"]: # If some emotions are above threshold
        # Check if 'neutral' is among the top if other scores are low
        neutral_score = result["all_emotion_scores"].get("neutral", 0)
        other_max_score = 0
        if result["active_emotions"]:
             # Find max score of non-neutral active emotions
             non_neutral_active = [em['score'] for em in result["active_emotions"] if em['emotion'] != 'neutral']
             if non_neutral_active:
                 other_max_score = max(non_neutral_active)

        # This assertion is tricky because "neutral" might not always win with highest score
        # even for neutral text, depending on model biases.
        # A better check might be that no strong non-neutral emotion is detected.
        assert neutral_score > 0.1 or other_max_score < 0.3 # Example condition
        print(f"Neutral score: {neutral_score}, Other max active score: {other_max_score}")
    else: # No active emotions above threshold
        assert result["dominant_emotion"] == "neutral"


def test_empty_string_input_goemotions():
    text = ""
    result = predict_emotion_goemotions(text, threshold=0.1)
    assert "error" not in result or result["error"] is None
    # Expect either no active emotions or 'neutral' as dominant
    assert not result["active_emotions"] or result["dominant_emotion"] == "neutral"
    print(f"Empty string result (GoEmotions): {result}")