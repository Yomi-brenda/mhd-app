# # models/emotion/model.py
# from transformers import AutoModelForSequenceClassification, AutoTokenizer
# import torch
# import torch.nn.functional as F

# class EmotionDetector:
#     def __init__(self, model_path=None):
#         if model_path:
#             self.tokenizer = AutoTokenizer.from_pretrained(model_path)
#             self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
#         else:
#             # Use a pre-trained emotion model
#             self.tokenizer = AutoTokenizer.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
#             self.model = AutoModelForSequenceClassification.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
        
#         self.emotions = ["sadness", "joy", "love", "anger", "fear", "surprise"]
    
#     def detect_emotion(self, text):
#         inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
#         with torch.no_grad():
#             outputs = self.model(**inputs)
        
#         probs = F.softmax(outputs.logits, dim=1).squeeze().tolist()
#         emotion_probs = {emotion: prob for emotion, prob in zip(self.emotions, probs)}
        
#         # Get most likely emotion
#         dominant_emotion = max(emotion_probs, key=emotion_probs.get)
#         confidence = emotion_probs[dominant_emotion]
        
#         return {
#             "dominant_emotion": dominant_emotion,
#             "confidence": confidence,
#             "all_emotions": emotion_probs
#         }