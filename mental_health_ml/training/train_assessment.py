# training/train_assessment.py
import torch
from torch.utils.data import DataLoader, Dataset
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from models.assessment.model import MentalHealthAssessmentModel
from data.preprocessing.assessment_preprocessing import AssessmentPreprocessor

class AssessmentDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item

    def __len__(self):
        return len(self.labels)

def train_assessment_model(train_data_path ="G:/mhd-app/mental_health_assessment_dataset.csv", num_epochs=5, batch_size=16, lr=2e-5):
    # Load and preprocess data
    data = pd.read_csv(train_data_path)
    preprocessor = AssessmentPreprocessor()
    
    # Extract features and labels
    X = data.drop(['anxiety_level', 'depression_level', 'stress_level', 'wellbeing_score', 'risk_level'], axis=1)
    y = data[['anxiety_level', 'depression_level', 'stress_level', 'wellbeing_score', 'risk_level']]
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Preprocess text
    train_encodings = preprocessor.preprocess_assessments(X_train)
    val_encodings = preprocessor.preprocess_assessments(X_val)
    
    # Create datasets
    train_dataset = AssessmentDataset(train_encodings, y_train.values)
    val_dataset = AssessmentDataset(val_encodings, y_val.values)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    # Initialize model
    model = MentalHealthAssessmentModel(num_labels=5)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    criterion = torch.nn.MSELoss()
    
    # Start MLflow tracking
    mlflow.start_run()
    mlflow.log_params({
        "model_type": "BERT-based assessment",
        "num_epochs": num_epochs,
        "batch_size": batch_size,
        "learning_rate": lr
    })
    
    # Training loop
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"]
            attention_mask = batch["attention_mask"]
            labels = batch["labels"].float()
            
            outputs = model(input_ids, attention_mask)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"]
                attention_mask = batch["attention_mask"]
                labels = batch["labels"].float()
                
                outputs = model(input_ids, attention_mask)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
        
        print(f"Epoch {epoch+1}: Train Loss: {train_loss/len(train_loader)}, Val Loss: {val_loss/len(val_loader)}")
        mlflow.log_metrics({
            "train_loss": train_loss/len(train_loader),
            "val_loss": val_loss/len(val_loader)
        }, step=epoch)
    
    # Save model
    torch.save(model.state_dict(), "models/assessment/assessment_model.pt")
    mlflow.pytorch.log_model(model, "assessment_model")
    mlflow.end_run()
    
    return model