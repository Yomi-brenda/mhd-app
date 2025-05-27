# mental_health_ml/data/preprocessing/prepare_chatbot_intent_data.py
import pandas as pd
from sklearn.model_selection import train_test_split
import os

FAQ_KB_PATH = "mental_health_ml/data/datasets/faq_kb.csv"
TRAIN_DATA_PATH = "mental_health_ml/data/processed/chatbot_intent_train.csv"
VAL_DATA_PATH = "mental_health_ml/data/processed/chatbot_intent_val.csv"
TEST_DATA_PATH = "mental_health_ml/data/processed/chatbot_intent_test.csv" # Optional, if you want a hold-out test set
LABEL_MAPPING_PATH = "mental_health_ml/data/processed/chatbot_intent_label_mapping.json" # To map intent_id to numerical labels

def create_intent_dataset(faq_kb_path: str):
    """
    Creates a dataset for intent classification from the FAQ KB.
    Each question variation becomes a row with its corresponding intent_id.
    """
    df_kb = pd.read_csv(faq_kb_path)
    
    all_data = []
    for _, row in df_kb.iterrows():
        intent_id = row['intent_id']
        variations = str(row['question_variations']).split('|')
        for variation in variations:
            if variation.strip(): # Ensure not empty
                all_data.append({'text': variation.strip().lower(), 'intent': intent_id})
    
    df_intent = pd.DataFrame(all_data)
    return df_intent

def save_label_mapping(df_intent: pd.DataFrame, mapping_path: str):
    """Saves the mapping from intent_id (string) to numerical labels."""
    intents = df_intent['intent'].unique()
    label2id = {label: i for i, label in enumerate(intents)}
    id2label = {i: label for label, i in label2id.items()}
    
    import json
    with open(mapping_path, 'w') as f:
        json.dump({'label2id': label2id, 'id2label': id2label}, f, indent=4)
    print(f"Label mapping saved to {mapping_path}")
    return label2id, id2label

if __name__ == "__main__":
    # Ensure output directories exist
    os.makedirs(os.path.dirname(TRAIN_DATA_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(LABEL_MAPPING_PATH), exist_ok=True)

    print(f"Processing FAQ KB from: {FAQ_KB_PATH}")
    df_intent_data = create_intent_dataset(FAQ_KB_PATH)
    print(f"Created dataset with {len(df_intent_data)} examples.")

    if df_intent_data.empty:
        print("No data generated. Exiting.")
    else:
        label2id, id2label = save_label_mapping(df_intent_data, LABEL_MAPPING_PATH)
        df_intent_data['label'] = df_intent_data['intent'].map(label2id)

        # Split data (e.g., 80% train, 20% validation/test)
        # For small FAQ KBs, might just use train/val and rely on out-of-sample testing.
        if len(df_intent_data) < 20: # If very few samples, simple split or use all for train.
            print("Warning: Very small dataset. Splitting might not be effective.")
            train_df = df_intent_data
            val_df = df_intent_data.sample(frac=0.2, random_state=42) if len(df_intent_data) > 5 else df_intent_data
            test_df = pd.DataFrame() # No separate test set for very small data
        else:
            train_df, temp_df = train_test_split(df_intent_data, test_size=0.3, random_state=42, stratify=df_intent_data['label'])
            val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label']) # Split temp into 50/50 val/test
            # This makes train 70%, val 15%, test 15% roughly

        train_df.to_csv(TRAIN_DATA_PATH, index=False)
        val_df.to_csv(VAL_DATA_PATH, index=False)
        if not test_df.empty:
            test_df.to_csv(TEST_DATA_PATH, index=False)
        
        print(f"Training data saved to {TRAIN_DATA_PATH} ({len(train_df)} examples)")
        print(f"Validation data saved to {VAL_DATA_PATH} ({len(val_df)} examples)")
        if not test_df.empty:
            print(f"Test data saved to {TEST_DATA_PATH} ({len(test_df)} examples)")
        else:
            print("No test data generated due to small dataset size.")
        
        print("\nUnique intents and their counts in the full dataset:")
        print(df_intent_data['intent'].value_counts())