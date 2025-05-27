# data/preprocessing/assessment_preprocessing.py
from transformers import BertTokenizer
import pandas as pd

class AssessmentPreprocessor:
    def __init__(self, max_length=128):
        self.tokenizer = BertTokenizer.from_pretrained("google/bert_uncased_L-4_H-512_A-8")
        self.max_length = max_length
        
    def preprocess(self, texts):
        """Preprocess a list of assessment responses"""
        encoded = self.tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        return {
            "input_ids": encoded["input_ids"],
            "attention_mask": encoded["attention_mask"]
        }
        
    def preprocess_assessments(self, assessment_df):
        """Process assessment dataframe with multiple question responses"""
        # Concatenate responses with question identifiers
        texts = []
        for _, row in assessment_df.iterrows():
            text = " ".join([f"Q{i+1}: {ans}" for i, ans in enumerate(row) if pd.notna(ans)])
            texts.append(text)
        return self.preprocess(texts)