# # models/crisis/model.py
# import re
# from transformers import AutoModelForSequenceClassification, AutoTokenizer
# import torch
# import torch.nn.functional as F

# class CrisisDetector:
#     def __init__(self, model_path=None, threshold=0.7):
#         self.threshold = threshold
        
#         if model_path:
#             self.tokenizer = AutoTokenizer.from_pretrained(model_path)
#             self.model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=2)
#         else:
#             # Use a general sentiment model as starting point (will need fine-tuning)
#             self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
#             self.model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
        
#         # Keyword patterns for rule-based checks
#         self.crisis_patterns = [
#             r"(?i)(?:want|going)\s+to\s+(?:kill|hurt)\s+(?:myself|me)",
#             r"(?i)sui[c]+ide",
#             r"(?i)(?:end|take)\s+my\s+life",
#             r"(?i)don't\s+want\s+to\s+live",
#             r"(?i)(?:better|easier)\s+(?:off|if)\s+(?:dead|gone|not here)"
#         ]
    
#     def detect_crisis(self, text):
#         # Rule-based detection
#         for pattern in self.crisis_patterns:
#             if re.search(pattern, text):
#                 return {
#                     "crisis_detected": True,
#                     "confidence": 0.95,  # High confidence for direct matches
#                     "method": "rule-based"
#                 }
        
#         # ML-based detection
#         inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
#         with torch.no_grad():
#             outputs = self.model(**inputs)
        
#         probs = F.softmax(outputs.logits, dim=1).squeeze().tolist()
#         crisis_prob = probs[1]  # Assuming binary classification with [no_crisis, crisis]
        
#         return {
#             "crisis_detected": crisis_prob > self.threshold,
#             "confidence": crisis_prob,
#             "method": "ml-based"
#         }