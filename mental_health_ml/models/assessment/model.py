# # models/assessment/model.py
# """
# Mental Health Assessment Model Implementation
# Combines BERT-based text analysis with numerical response processing
# """

# import torch
# import torch.nn as nn
# from transformers import BertModel, BertTokenizer
# import numpy as np
# from typing import Dict, List, Optional, Tuple
# import logging

# logger = logging.getLogger(__name__)

# class MentalHealthAssessmentModel(nn.Module):
#     """
#     Multi-modal mental health assessment model that processes both:
#     1. Numerical survey responses (1-10 scale questions)
#     2. Text responses (open-ended comments)
#     """
    
#     def __init__(self, 
#                  num_numerical_features: int = 10,
#                  num_labels: int = 5,
#                  bert_model_name: str = "google/bert_uncased_L-4_H-512_A-8",
#                  dropout_rate: float = 0.1,
#                  hidden_size: int = 256):
#         """
#         Initialize the assessment model
        
#         Args:
#             num_numerical_features: Number of numerical survey questions
#             num_labels: Number of output labels (anxiety, depression, stress, wellbeing, risk)
#             bert_model_name: Pre-trained BERT model to use
#             dropout_rate: Dropout rate for regularization
#             hidden_size: Hidden layer size for numerical features
#         """
#         super().__init__()
        
#         self.num_numerical_features = num_numerical_features
#         self.num_labels = num_labels
        
#         # BERT for text processing
#         try:
#             self.bert = BertModel.from_pretrained(bert_model_name)
#             self.bert_hidden_size = self.bert.config.hidden_size
#             logger.info(f"Loaded BERT model: {bert_model_name}")
#         except Exception as e:
#             logger.warning(f"Could not load {bert_model_name}, using base model")
#             self.bert = BertModel.from_pretrained("bert-base-uncased")
#             self.bert_hidden_size = self.bert.config.hidden_size
        
#         # Freeze early BERT layers to reduce training time
#         for param in list(self.bert.parameters())[:-12]:  # Freeze all but last 2 layers
#             param.requires_grad = False
        
#         # Numerical features processing
#         self.numerical_processor = nn.Sequential(
#             nn.Linear(num_numerical_features, hidden_size),
#             nn.ReLU(),
#             nn.Dropout(dropout_rate),
#             nn.Linear(hidden_size, hidden_size // 2),
#             nn.ReLU(),
#             nn.Dropout(dropout_rate)
#         )
        
#         # Text features processing
#         self.text_processor = nn.Sequential(
#             nn.Linear(self.bert_hidden_size, hidden_size),
#             nn.ReLU(),
#             nn.Dropout(dropout_rate),
#             nn.Linear(hidden_size, hidden_size // 2),
#             nn.ReLU(),
#             nn.Dropout(dropout_rate)
#         )
        
#         # Combined features processing
#         combined_size = (hidden_size // 2) * 2  # numerical + text features
#         self.classifier = nn.Sequential(
#             nn.Linear(combined_size, hidden_size),
#             nn.ReLU(),
#             nn.Dropout(dropout_rate),
#             nn.Linear(hidden_size, hidden_size // 2),
#             nn.ReLU(),
#             nn.Dropout(dropout_rate),
#             nn.Linear(hidden_size // 2, num_labels),
#             nn.Sigmoid()  # Output probabilities between 0 and 1
#         )
        
#         # Initialize weights
#         self._init_weights()
    
#     def _init_weights(self):
#         """Initialize model weights"""
#         for module in [self.numerical_processor, self.text_processor, self.classifier]:
#             for layer in module:
#                 if isinstance(layer, nn.Linear):
#                     torch.nn.init.xavier_uniform_(layer.weight)
#                     torch.nn.init.zeros_(layer.bias)
    
#     def forward(self, 
#                 numerical_features: torch.Tensor,
#                 input_ids: Optional[torch.Tensor] = None,
#                 attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
#         """
#         Forward pass of the model
        
#         Args:
#             numerical_features: Tensor of shape (batch_size, num_numerical_features)
#             input_ids: BERT input token IDs (batch_size, seq_len)
#             attention_mask: BERT attention mask (batch_size, seq_len)
            
#         Returns:
#             Tensor of shape (batch_size, num_labels) with predictions
#         """
#         batch_size = numerical_features.shape[0]
        
#         # Process numerical features
#         numerical_output = self.numerical_processor(numerical_features)
        
#         # Process text features if provided
#         if input_ids is not None and attention_mask is not None:
#             bert_outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
#             text_features = bert_outputs.pooler_output
#             text_output = self.text_processor(text_features)
#         else:
#             # If no text provided, use zeros
#             text_output = torch.zeros(batch_size, self.numerical_processor[-2].out_features).to(numerical_features.device)
        
#         # Combine features
#         combined_features = torch.cat([numerical_output, text_output], dim=1)
        
#         # Final classification
#         predictions = self.classifier(combined_features)
        
#         return predictions
    
#     def predict_labels(self, predictions: torch.Tensor) -> Dict[str, float]:
#         """
#         Convert model predictions to interpretable labels
        
#         Args:
#             predictions: Model output tensor
            
#         Returns:
#             Dictionary with label names and values
#         """
#         if len(predictions.shape) > 1:
#             predictions = predictions.squeeze()
        
#         pred_np = predictions.detach().cpu().numpy()
        
#         return {
#             'anxiety_level': float(pred_np[0]),
#             'depression_level': float(pred_np[1]),
#             'stress_level': float(pred_np[2]),
#             'wellbeing_score': float(pred_np[3]),
#             'risk_level': float(pred_np[4])
#         }
    
#     def get_recommendations(self, predictions: Dict[str, float]) -> List[str]:
#         """
#         Generate recommendations based on assessment results
        
#         Args:
#             predictions: Dictionary of predicted labels
            
#         Returns:
#             List of recommendation strings
#         """
#         recommendations = []
        
#         # Anxiety recommendations
#         if predictions['anxiety_level'] > 0.7:
#             recommendations.extend([
#                 "Practice deep breathing exercises for 5-10 minutes daily",
#                 "Consider trying progressive muscle relaxation techniques",
#                 "Limit caffeine intake, especially in the afternoon"
#             ])
#         elif predictions['anxiety_level'] > 0.5:
#             recommendations.append("Try mindfulness meditation to help manage worry")
        
#         # Depression recommendations
#         if predictions['depression_level'] > 0.7:
#             recommendations.extend([
#                 "Consider scheduling a consultation with a mental health professional",
#                 "Try to maintain a regular sleep schedule",
#                 "Engage in light physical activity, even if just a short walk"
#             ])
#         elif predictions['depression_level'] > 0.5:
#             recommendations.extend([
#                 "Connect with friends or family members",
#                 "Consider keeping a mood journal"
#             ])
        
#         # Stress recommendations
#         if predictions['stress_level'] > 0.6:
#             recommendations.extend([
#                 "Practice time management techniques",
#                 "Set boundaries between work and personal time",
#                 "Try stress-relief activities like yoga or listening to music"
#             ])
        
#         # Wellbeing recommendations
#         if predictions['wellbeing_score'] < 0.4:
#             recommendations.extend([
#                 "Focus on self-care activities that bring you joy",
#                 "Consider exploring new hobbies or interests",
#                 "Make time for activities that give you a sense of accomplishment"
#             ])
        
#         # Risk recommendations
#         if predictions['risk_level'] > 0.6:
#             recommendations.extend([
#                 "Please consider reaching out to a crisis helpline for immediate support",
#                 "Contact a mental health professional as soon as possible",
#                 "Reach out to trusted friends, family, or support groups"
#             ])
        
#         # General wellness recommendations
#         if len(recommendations) == 0:
#             recommendations.extend([
#                 "Maintain a balanced lifestyle with regular exercise and healthy eating",
#                 "Practice gratitude by writing down three things you're thankful for daily",
#                 "Stay connected with supportive people in your life"
#             ])
        
#         return recommendations[:5]  # Limit to top 5 recommendations

# class AssessmentPreprocessor:
#     """
#     Preprocessor for assessment data handling both numerical and text inputs
#     """
    
#     def __init__(self, 
#                  bert_model_name: str = "google/bert_uncased_L-4_H-512_A-8",
#                  max_length: int = 128):
#         """
#         Initialize the preprocessor
        
#         Args:
#             bert_model_name: BERT model for tokenization
#             max_length: Maximum sequence length for text
#         """
#         try:
#             self.tokenizer = BertTokenizer.from_pretrained(bert_model_name)
#         except:
#             logger.warning(f"Could not load tokenizer for {bert_model_name}, using base")
#             self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
            
#         self.max_length = max_length
        
#         # Define expected numerical features order
#         self.numerical_features_order = [
#             'q1_mood', 'q2_anxiety', 'q3_sleep', 'q4_energy', 'q5_concentration',
#             'q6_social', 'q7_appetite', 'q8_hopelessness', 'q9_worthlessness', 'q10_stress'
#         ]
        
#     def preprocess_single_assessment(self, responses: Dict) -> Dict[str, torch.Tensor]:
#         """
#         Preprocess a single assessment response
        
#         Args:
#             responses: Dictionary containing assessment responses
            
#         Returns:
#             Dictionary with preprocessed tensors
#         """
#         # Extract numerical features
#         numerical_values = []
#         for feature in self.numerical_features_order:
#             value = responses.get(feature, 5)  # Default to neutral (5) if missing
#             # Normalize to 0-1 range
#             normalized_value = (float(value) - 1) / 9.0
#             numerical_values.append(normalized_value)
        
#         numerical_tensor = torch.FloatTensor(numerical_values).unsqueeze(0)
        
#         result = {'numerical_features': numerical_tensor}
        
#         # Process text if available
#         text_content = responses.get('additional_comments', '')
#         if text_content and text_content.strip():
#             encoded = self.tokenizer(
#                 text_content,
#                 padding='max_length',
#                 truncation=True,
#                 max_length=self.max_length,
#                 return_tensors='pt'
#             )
#             result['input_ids'] = encoded['input_ids']
#             result['attention_mask'] = encoded['attention_mask']
        
#         return result
    
#     def preprocess_batch(self, responses_list: List[Dict]) -> Dict[str, torch.Tensor]:
#         """
#         Preprocess a batch of assessment responses
        
#         Args:
#             responses_list: List of response dictionaries
            
#         Returns:
#             Dictionary with batched tensors
#         """
#         batch_numerical = []
#         batch_texts = []
#         has_text = []
        
#         for responses in responses_list:
#             # Process numerical features
#             numerical_values = []
#             for feature in self.numerical_features_order:
#                 value = responses.get(feature, 5)
#                 normalized_value = (float(value) - 1) / 9.0
#                 numerical_values.append(normalized_value)
#             batch_numerical.append(numerical_values)
            
#             # Collect text
#             text_content = responses.get('additional_comments', '')
#             batch_texts.append(text_content if text_content.strip() else '')
#             has_text.append(bool(text_content.strip()))
        
#         result = {
#             'numerical_features': torch.FloatTensor(batch_numerical)
#         }
        
#         # Process text if any samples have text
#         if any(has_text):
#             encoded = self.tokenizer(
#                 batch_texts,
#                 padding='max_length',
#                 truncation=True,
#                 max_length=self.max_length,
#                 return_tensors='pt'
#             )
#             result['input_ids'] = encoded['input_ids']
#             result['attention_mask'] = encoded['attention_mask']
        
#         return result