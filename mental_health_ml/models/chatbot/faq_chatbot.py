# mental_health_ml/models/chatbot/faq_chatbot.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
import json
import os
import random

# --- Configuration ---
# These should point to the *best* trained model artifacts
MODEL_PATH = "saved_models/chatbot/intent_classifier_distilbert-base-uncased_intent_classifier_best_epoch3" # Example path, update after training
LABEL_MAPPING_PATH = "mental_health_ml/data/processed/chatbot_intent_label_mapping.json"
FAQ_KB_PATH = "mental_health_ml/data/datasets/faq_kb.csv"
MAX_LENGTH = 128
# --- End Configuration ---

class FAQChatbot:
    def __init__(self, model_path, label_mapping_path, faq_kb_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"FAQChatbot using device: {self.device}")

        if not os.path.exists(model_path) or \
           not os.path.exists(label_mapping_path) or \
           not os.path.exists(faq_kb_path):
            raise FileNotFoundError(
                f"One or more required files not found. Searched: "
                f"Model: {model_path}, Labels: {label_mapping_path}, KB: {faq_kb_path}"
            )

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path).to(self.device)
        self.model.eval() # Set to evaluation mode

        with open(label_mapping_path, 'r') as f:
            label_map = json.load(f)
        self.id2label = {int(k): v for k, v in label_map['id2label'].items()} # Ensure keys are int

        self.faq_kb = pd.read_csv(faq_kb_path)
        # Create a quick lookup for answers by intent_id
        self.answer_lookup = self.faq_kb.set_index('intent_id')['answer'].to_dict()
        self.default_fallback_intent = "default_fallback" # Ensure this intent_id exists in your KB

        print("FAQChatbot initialized successfully.")

    def predict_intent(self, text: str) -> tuple[str, float]:
        """Predicts the intent of a given text."""
        inputs = self.tokenizer.encode_plus(
            text.lower().strip(),
            add_special_tokens=True,
            max_length=MAX_LENGTH,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
        
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1).cpu().numpy()[0]
        predicted_label_id = np.argmax(probabilities)
        confidence = probabilities[predicted_label_id]
        
        predicted_intent_id = self.id2label.get(predicted_label_id, self.default_fallback_intent)
        
        return predicted_intent_id, float(confidence)

    def get_answer(self, intent_id: str) -> str:
        """Retrieves an answer from the KB for a given intent_id."""
        answer = self.answer_lookup.get(intent_id)
        if not answer:
            # Fallback if intent is somehow predicted but not in answer_lookup (should not happen with good KB)
            answer = self.answer_lookup.get(self.default_fallback_intent, "I'm sorry, I don't have an answer for that right now.")
        return answer

    def get_response(self, user_message: str, confidence_threshold: float = 0.65) -> dict:
        """
        Gets a response for a user message by predicting intent and retrieving an answer.
        """
        predicted_intent, confidence = self.predict_intent(user_message)
        
        print(f"User: '{user_message}' -> Predicted Intent: '{predicted_intent}' (Confidence: {confidence:.4f})")

        if confidence < confidence_threshold:
            final_intent = self.default_fallback_intent
            print(f"  Confidence below threshold ({confidence_threshold}). Using fallback intent.")
        else:
            final_intent = predicted_intent
        
        bot_response = self.get_answer(final_intent)
        
        return {
            "user_message": user_message,
            "predicted_intent": predicted_intent, # Original predicted intent
            "intent_confidence": confidence,
            "final_intent_used": final_intent, # Intent used after thresholding
            "bot_response": bot_response,
            "model_version_tag": f"intent_classifier_loaded_from_{os.path.basename(MODEL_PATH)}"
        }

if __name__ == "__main__":
    # --- IMPORTANT ---
    # Before running this, ensure you have:
    # 1. Run `prepare_chatbot_intent_data.py` to generate `faq_kb.csv` and label mapping.
    # 2. Run `train_chatbot_intent_classifier.py` to train a model and save it.
    # 3. UPDATE THE `MODEL_PATH` variable above to point to your *actual trained model directory*.
    #    For example: "saved_models/chatbot/intent_classifier_distilbert-base-uncased_intent_classifier_best_epoch3"
    # ---

    # Check if the default MODEL_PATH exists, otherwise prompt user
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Trained model not found at the default path: {MODEL_PATH}")
        print("Please train an intent classifier model first using 'train_chatbot_intent_classifier.py'")
        print("Then, update the MODEL_PATH variable in 'faq_chatbot.py' to point to your saved model directory.")
        exit()
    
    chatbot = FAQChatbot(
        model_path=MODEL_PATH,
        label_mapping_path=LABEL_MAPPING_PATH,
        faq_kb_path=FAQ_KB_PATH
    )

    test_queries = [
        "Hello there!",
        "what is anxiety?",
        "I'm feeling really sad today", # Might map to feeling_sad intent
        "how can i manage stress?",
        "tell me about this application",
        "thanks a lot",
        "sdlkfjsdlf", # Should fallback
        "goodbye"
    ]

    for query in test_queries:
        response_data = chatbot.get_response(query, confidence_threshold=0.6) # Adjust threshold as needed
        print(f"  User: {query}")
        print(f"  Bot: {response_data['bot_response']}")
        print(f"  (Debug: Original Intent: {response_data['predicted_intent']}, Conf: {response_data['intent_confidence']:.2f}, Final Intent: {response_data['final_intent_used']})")
        print("-" * 30)