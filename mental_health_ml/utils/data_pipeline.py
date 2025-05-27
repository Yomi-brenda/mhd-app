# utils/data_pipeline.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import re
from datetime import datetime

class DataPipeline:
    def __init__(self):
        self.preprocessing_steps = []
        
    def add_preprocessing_step(self, step_func, **kwargs):
        """Add a preprocessing step to the pipeline"""
        self.preprocessing_steps.append((step_func, kwargs))
        
    def process(self, data):
        """Apply all preprocessing steps to data"""
        for step_func, kwargs in self.preprocessing_steps:
            data = step_func(data, **kwargs)
        return data

# Text preprocessing functions
def clean_text(text: str) -> str:
    """Basic text cleaning"""
    if not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\!\?\,\;\:]', '', text)
    
    # Convert to lowercase
    text = text.lower().strip()
    
    return text

def anonymize_personal_info(text: str) -> str:
    """Remove or mask personal information from text"""
    if not isinstance(text, str):
        return ""
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Remove potential names (very basic - would need more sophisticated NER)
    # This is a simple approach, in production use proper NER models
    text = re.sub(r'\bmy name is \w+\b', 'my name is [NAME]', text, flags=re.IGNORECASE)
    
    return text

def extract_emotional_keywords(text: str) -> List[str]:
    """Extract emotional keywords from text"""
    emotion_keywords = {
        'positive': ['happy', 'joy', 'excited', 'grateful', 'content', 'peaceful', 'confident'],
        'negative': ['sad', 'angry', 'frustrated', 'worried', 'anxious', 'depressed', 'stressed'],
        'crisis': ['suicide', 'kill myself', 'end it all', 'hopeless', 'worthless']
    }
    
    found_keywords = []
    text_lower = text.lower()
    
    for category, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append((keyword, category))
    
    return found_keywords