# initialize_models.py
import torch
import os
from models.assessment.model import MentalHealthAssessmentModel
from models.chatbot.model import MentalHealthChatbot
from models.emotion.model import EmotionDetector
from models.crisis.model import CrisisDetector

def initialize_all_models():
    print("Initializing ML models...")
    
    # Initialize assessment model
    assessment_path = "models/assessment/assessment_model.pt"
    if os.path.exists(assessment_path):
        print("Loading assessment model from", assessment_path)
        # Initialize model here
    else:
        print("Assessment model not found. Using base model.")
        
    # Initialize chatbot
    print("Initializing chatbot model...")
    chatbot = MentalHealthChatbot()
    
    # Initialize emotion detector
    print("Initializing emotion detection model...")
    emotion_detector = EmotionDetector()
    
    # Initialize crisis detector
    print("Initializing crisis detection model...")
    crisis_detector = CrisisDetector()
    
    print("All models initialized successfully")

if __name__ == "__main__":
    initialize_all_models()