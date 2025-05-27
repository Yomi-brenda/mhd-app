# training/prepare_data.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from utils.data_pipeline import DataPipeline, clean_text, anonymize_personal_info
import json

def prepare_assessment_data(data_file: str, output_dir: str):
    """Prepare assessment data for training"""
    # Load raw data
    with open(data_file, 'r') as f:
        raw_data = json.load(f)
    
    # Filter assessment data
    assessment_data = [d for d in raw_data if d['data_type'] == 'assessment']
    
    # Convert to DataFrame
    processed_data = []
    for item in assessment_data:
        row = {
            'user_id': item['user_id'],
            'timestamp': item['timestamp']
        }
        
        # Add responses
        for q_id, response in item['responses'].items():
            row[f'response_{q_id}'] = clean_text(str(response))
        
        # Add labels if available
        if item.get('labels'):
            for label, value in item['labels'].items():
                row[label] = value
        
        processed_data.append(row)
    
    df = pd.DataFrame(processed_data)
    
    # Split data
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # Save prepared data
    train_df.to_csv(f"{output_dir}/assessment_train.csv", index=False)
    test_df.to_csv(f"{output_dir}/assessment_test.csv", index=False)
    
    print(f"Assessment data prepared: {len(train_df)} train, {len(test_df)} test samples")
    
def prepare_conversation_data(data_file: str, output_dir: str):
    """Prepare conversation data for chatbot training"""
    with open(data_file, 'r') as f:
        raw_data = json.load(f)
    
    # Filter conversation data
    conversation_data = [d for d in raw_data if d['data_type'] == 'conversation']
    
    # Convert conversations to training format
    training_pairs = []
    for item in conversation_data:
        conversation = item['conversation']
        
        # Create input-output pairs
        for i in range(len(conversation) - 1):
            if (conversation[i]['role'] == 'user' and 
                conversation[i+1]['role'] == 'assistant'):
                
                training_pairs.append({
                    'input': clean_text(conversation[i]['content']),
                    'output': clean_text(conversation[i+1]['content']),
                    'user_id': item['user_id'],
                    'timestamp': conversation[i]['timestamp']
                })
    
    df = pd.DataFrame(training_pairs)
    
    # Split data
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # Save prepared data
    train_df.to_csv(f"{output_dir}/conversation_train.csv", index=False)
    test_df.to_csv(f"{output_dir}/conversation_test.csv", index=False)
    
    print(f"Conversation data prepared: {len(train_df)} train, {len(test_df)} test samples")

if __name__ == "__main__":
    import os
    
    # Create output directory
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare data (assuming you have collected data)
    if os.path.exists("data/collected/training_data.json"):
        prepare_assessment_data("data/collected/training_data.json", output_dir)
        prepare_conversation_data("data/collected/training_data.json", output_dir)
    else:
        print("No training data found. Please collect data first.")