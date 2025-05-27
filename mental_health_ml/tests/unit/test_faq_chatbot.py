# mental_health_ml/tests/unit/test_faq_chatbot.py
import pytest
from unittest.mock import patch, MagicMock
import torch
import numpy as np
import pandas as pd
import os
import json

# Mock data paths (these files should exist for the test setup or be mocked)
# For tests, we create minimal dummy versions of these.
TEST_MODEL_PATH = "mental_health_ml/tests/unit/test_data/dummy_intent_model"
TEST_LABEL_MAPPING_PATH = "mental_health_ml/tests/unit/test_data/dummy_intent_label_mapping.json"
TEST_FAQ_KB_PATH = "mental_health_ml/tests/unit/test_data/dummy_faq_kb.csv"


@pytest.fixture(scope="module", autouse=True)
def create_dummy_chatbot_artifacts():
    # Create dummy directories and files needed by the chatbot for tests
    os.makedirs(TEST_MODEL_PATH, exist_ok=True)
    # Mock tokenizer and model save_pretrained behavior by creating dummy files they expect
    # For a real test with a model, you'd save a tiny dummy model.
    # Here, we'll mostly mock the transformers.Auto... calls in the chatbot's __init__

    # Dummy label mapping
    dummy_label_map = {
        "label2id": {"greet": 0, "def_anxiety": 1, "default_fallback": 2},
        "id2label": {"0": "greet", "1": "def_anxiety", "2": "default_fallback"}
    }
    with open(TEST_LABEL_MAPPING_PATH, 'w') as f:
        json.dump(dummy_label_map, f)

    # Dummy FAQ KB
    dummy_faq_data = {
        "intent_id": ["greet", "def_anxiety", "default_fallback"],
        "question_variations": ["hi", "what is anxiety", "blah"],
        "answer": ["Hello test!", "Anxiety is a test feeling.", "Test fallback."]
    }
    pd.DataFrame(dummy_faq_data).to_csv(TEST_FAQ_KB_PATH, index=False)

    # Dummy model config (transformers expects config.json)
    dummy_config = {"architectures": ["DistilBertForSequenceClassification"], "id2label": dummy_label_map["id2label"], "label2id": dummy_label_map["label2id"]}
    with open(os.path.join(TEST_MODEL_PATH, "config.json"), 'w') as f:
        json.dump(dummy_config, f)
    # Dummy tokenizer files (vocab.txt for Bert/DistilBert based)
    with open(os.path.join(TEST_MODEL_PATH, "vocab.txt"), 'w') as f:
        f.write("[UNK]\n[CLS]\n[SEP]\nhello\nworld\n") # Minimal vocab
    # Dummy model file (pytorch_model.bin) - just an empty file for path existence
    open(os.path.join(TEST_MODEL_PATH, "pytorch_model.bin"), 'w').close()


    yield # Tests run here

    # Teardown: remove dummy files
    os.remove(TEST_LABEL_MAPPING_PATH)
    os.remove(TEST_FAQ_KB_PATH)
    os.remove(os.path.join(TEST_MODEL_PATH, "config.json"))
    os.remove(os.path.join(TEST_MODEL_PATH, "vocab.txt"))
    os.remove(os.path.join(TEST_MODEL_PATH, "pytorch_model.bin"))
    os.rmdir(TEST_MODEL_PATH)
    # Clean up directory if it's empty
    test_data_dir = os.path.dirname(TEST_MODEL_PATH)
    if not os.listdir(test_data_dir):
        os.rmdir(test_data_dir)


# We need to import the class *after* the paths are defined for the module-level fixture
# This is a bit tricky with fixtures. A common way is to put imports inside test functions
# or ensure fixtures modify paths known to the imported module *before* it's imported.
# For simplicity here, we assume FAQChatbot is imported after fixture setup or can handle these paths.

def test_chatbot_initialization():
    from mental_health_ml.models.chatbot.faq_chatbot import FAQChatbot # Import here after fixture setup
    chatbot = FAQChatbot(
        model_path=TEST_MODEL_PATH,
        label_mapping_path=TEST_LABEL_MAPPING_PATH,
        faq_kb_path=TEST_FAQ_KB_PATH
    )
    assert chatbot is not None
    assert "greet" in chatbot.answer_lookup

def test_chatbot_get_known_intent():
    from mental_health_ml.models.chatbot.faq_chatbot import FAQChatbot
    chatbot = FAQChatbot(TEST_MODEL_PATH, TEST_LABEL_MAPPING_PATH, TEST_FAQ_KB_PATH)

    # Mock the model's output for predict_intent
    # Let's say 'hi' predicts 'greet' with high confidence
    mock_logits = torch.tensor([[0.1, 0.1, 0.8]]) # Assuming 'greet' is label index 0 based on dummy mapping (adjusted)
    # Correcting dummy_label_map: "greet": 0, "def_anxiety": 1, "default_fallback": 2
    # So, for "greet", the highest logit should be at index 0
    mock_logits_greet = torch.tensor([[0.8, 0.1, 0.1]]) # High score for 'greet' (index 0)

    with patch.object(chatbot.model, 'forward', return_value=MagicMock(logits=mock_logits_greet.to(chatbot.device))) as mock_forward, \
         patch.object(chatbot.model, '__call__', return_value=MagicMock(logits=mock_logits_greet.to(chatbot.device))) as mock_call: # Also mock __call__

        response_data = chatbot.get_response("hi", confidence_threshold=0.5)
        # mock_forward.assert_called_once() # or mock_call
        assert response_data["final_intent_used"] == "greet"
        assert response_data["bot_response"] == "Hello test!"

def test_chatbot_low_confidence_fallback():
    from mental_health_ml.models.chatbot.faq_chatbot import FAQChatbot
    chatbot = FAQChatbot(TEST_MODEL_PATH, TEST_LABEL_MAPPING_PATH, TEST_FAQ_KB_PATH)

    # Mock model output for low confidence
    # Scores: greet=0.2, def_anxiety=0.1, default_fallback=0.1
    mock_logits_low_conf = torch.tensor([[0.2, 0.1, 0.1]])

    with patch.object(chatbot.model, 'forward', return_value=MagicMock(logits=mock_logits_low_conf.to(chatbot.device))) as mock_forward, \
         patch.object(chatbot.model, '__call__', return_value=MagicMock(logits=mock_logits_low_conf.to(chatbot.device))) as mock_call:

        response_data = chatbot.get_response("unknown query", confidence_threshold=0.5)
        assert response_data["final_intent_used"] == "default_fallback"
        assert response_data["bot_response"] == "Test fallback."
        assert response_data["intent_confidence"] < 0.5 # Check original confidence

def test_chatbot_unknown_intent_direct_fallback():
    from mental_health_ml.models.chatbot.faq_chatbot import FAQChatbot
    chatbot = FAQChatbot(TEST_MODEL_PATH, TEST_LABEL_MAPPING_PATH, TEST_FAQ_KB_PATH)

    # Mock model to predict the fallback intent directly (e.g. if input is gibberish)
    # Scores: greet=0.1, def_anxiety=0.1, default_fallback=0.8
    mock_logits_fallback = torch.tensor([[0.1, 0.1, 0.8]])

    with patch.object(chatbot.model, 'forward', return_value=MagicMock(logits=mock_logits_fallback.to(chatbot.device))) as mock_forward, \
         patch.object(chatbot.model, '__call__', return_value=MagicMock(logits=mock_logits_fallback.to(chatbot.device))) as mock_call:
        response_data = chatbot.get_response("gibberish input", confidence_threshold=0.5)
        assert response_data["final_intent_used"] == "default_fallback" # Because it was predicted with high conf
        assert response_data["bot_response"] == "Test fallback."

# It's good practice to also test predict_intent and get_answer methods directly if they have complex logic.