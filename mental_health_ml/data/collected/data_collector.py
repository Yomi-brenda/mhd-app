# data/collection/data_collector.py
import pandas as pd
import numpy as np
from typing import List, Dict
import json
from datetime import datetime
import hashlib

class MentalHealthDataCollector:
    def __init__(self, anonymize=True):
        self.anonymize = anonymize
        self.collected_data = []
        
    def collect_assessment_response(self, user_id: str, responses: Dict, labels: Dict = None):
        """Collect assessment responses for training data"""
        # Create anonymous user ID
        if self.anonymize:
            anon_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        else:
            anon_id = user_id
            
        data_point = {
            'user_id': anon_id,
            'timestamp': datetime.now().isoformat(),
            'responses': responses,
            'labels': labels,
            'data_type': 'assessment'
        }
        
        self.collected_data.append(data_point)
        
    def collect_conversation_data(self, user_id: str, conversation: List[Dict], 
                                feedback: Dict = None):
        """Collect conversation data for chatbot training"""
        if self.anonymize:
            anon_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        else:
            anon_id = user_id
            
        # Anonymize conversation content
        anonymized_conversation = []
        for msg in conversation:
            anonymized_msg = {
                'role': msg['role'],
                'content': self.anonymize_text(msg['content']) if self.anonymize else msg['content'],
                'timestamp': msg.get('timestamp', datetime.now().isoformat())
            }
            anonymized_conversation.append(anonymized_msg)
            
        data_point = {
            'user_id': anon_id,
            'timestamp': datetime.now().isoformat(),
            'conversation': anonymized_conversation,
            'feedback': feedback,
            'data_type': 'conversation'
        }
        
        self.collected_data.append(data_point)
        
    def anonymize_text(self, text: str) -> str:
        """Anonymize sensitive information in text"""
        # Use the anonymization function from data pipeline
        from utils.data_pipeline import anonymize_personal_info
        return anonymize_personal_info(text)
        
    def export_data(self, filename: str, format='json'):
        """Export collected data to file"""
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(self.collected_data, f, indent=2)
        elif format == 'csv':
            df = pd.DataFrame(self.collected_data)
            df.to_csv(filename, index=False)
        else:
            raise ValueError("Format must be 'json' or 'csv'")
            
    def get_training_data(self, data_type: str = None):
        """Get training data filtered by type"""
        if data_type:
            return [d for d in self.collected_data if d['data_type'] == data_type]
        return self.collected_data