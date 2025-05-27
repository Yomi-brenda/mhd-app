# evaluation/assess_model_eval.py
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

class AssessmentModelEvaluator:
    def __init__(self, model, preprocessor):
        self.model = model
        self.preprocessor = preprocessor
        
    def evaluate(self, test_data_path: str):
        """Evaluate assessment model on test data"""
        # Load test data
        test_df = pd.read_csv(test_data_path)
        
        # Separate features and labels
        feature_cols = [col for col in test_df.columns if col.startswith('response_')]
        label_cols = ['anxiety_level', 'depression_level', 'stress_level', 
                     'wellbeing_score', 'risk_level']
        
        X_test = test_df[feature_cols]
        y_test = test_df[label_cols]
        
        # Preprocess test data
        test_encodings = self.preprocessor.preprocess_assessments(X_test)
        
        # Get predictions
        import torch
        self.model.eval()
        with torch.no_grad():
            predictions = self.model(
                test_encodings["input_ids"],
                test_encodings["attention_mask"]
            ).numpy()
        
        # Calculate metrics
        metrics = {}
        for i, label in enumerate(label_cols):
            y_true = y_test[label].values
            y_pred = predictions[:, i]
            
            metrics[label] = {
                'mse': mean_squared_error(y_true, y_pred),
                'mae': mean_absolute_error(y_true, y_pred),
                'r2': r2_score(y_true, y_pred)
            }
        
        return metrics, predictions, y_test.values
        
    def plot_results(self, metrics, predictions, y_true, label_names):
        """Plot evaluation results"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, label in enumerate(label_names):
            if i < len(axes):
                # Scatter plot of true vs predicted
                axes[i].scatter(y_true[:, i], predictions[:, i], alpha=0.6)
                axes[i].plot([y_true[:, i].min(), y_true[:, i].max()], 
                            [y_true[:, i].min(), y_true[:, i].max()], 'r--', lw=2)
                axes[i].set_xlabel('True Values')
                axes[i].set_ylabel('Predictions')
                axes[i].set_title(f'{label}\nR² = {metrics[label]["r2"]:.3f}')
        
        plt.tight_layout()
        plt.savefig('evaluation/assessment_evaluation.png')
        plt.show()