# mental_health_ml/training/train_chatbot_intent_classifier.py
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AdamW, get_linear_schedule_with_warmup
from sklearn.metrics import accuracy_score, f1_score, classification_report
import numpy as np
import pandas as pd
import json
import mlflow
import mlflow.pytorch
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
MODEL_NAME = "distilbert-base-uncased" # Small and efficient for intent classification
TRAIN_DATA_PATH = "mental_health_ml/data/processed/chatbot_intent_train.csv"
VAL_DATA_PATH = "mental_health_ml/data/processed/chatbot_intent_val.csv"
LABEL_MAPPING_PATH = "mental_health_ml/data/processed/chatbot_intent_label_mapping.json"
TEXT_COLUMN = "text"
LABEL_COLUMN = "label" # Numerical label column created by preprocessing script

# Hyperparameters
EPOCHS = 5 # Adjust based on dataset size and convergence
BATCH_SIZE = 8
LEARNING_RATE = 2e-5
MAX_LENGTH = 128 # Max sequence length for intent utterances

# MLflow settings
MLFLOW_EXPERIMENT_NAME = "Chatbot_Intent_Classification"
MLFLOW_RUN_NAME = f"{MODEL_NAME}_intent_classifier"
# --- End Configuration ---

class IntentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        return {
            'text': text, # Keep original text for potential error analysis
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long) # CrossEntropyLoss expects long
        }

def compute_metrics(preds, labels, label_names):
    preds_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    acc = accuracy_score(labels_flat, preds_flat)
    f1_macro = f1_score(labels_flat, preds_flat, average='macro', zero_division=0)
    f1_weighted = f1_score(labels_flat, preds_flat, average='weighted', zero_division=0)
    
    print("\n--- Classification Report (Intent) ---")
    try:
        report = classification_report(labels_flat, preds_flat, target_names=label_names, zero_division=0)
        print(report)
        with open("intent_classification_report.txt", "w") as f:
            f.write(report)
        mlflow.log_artifact("intent_classification_report.txt")
    except Exception as e:
        print(f"Could not generate full classification report for intents: {e}")

    return {"accuracy": acc, "f1_macro": f1_macro, "f1_weighted": f1_weighted}

def train_epoch(model, data_loader, loss_fn, optimizer, device, scheduler):
    model = model.train()
    losses = []
    for batch_idx, d in enumerate(data_loader):
        input_ids = d["input_ids"].to(device)
        attention_mask = d["attention_mask"].to(device)
        labels = d["labels"].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        losses.append(loss.item())
        loss.backward()
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()
        if batch_idx % 5 == 0:
             print(f"  Batch {batch_idx+1}/{len(data_loader)}, Loss: {loss.item():.4f}")
    return np.mean(losses)

def eval_model(model, data_loader, loss_fn, device, label_names):
    model = model.eval()
    losses = []
    all_logits = []
    all_labels = []
    with torch.no_grad():
        for d in data_loader:
            input_ids = d["input_ids"].to(device)
            attention_mask = d["attention_mask"].to(device)
            labels = d["labels"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            logits = outputs.logits
            losses.append(loss.item())
            all_logits.append(logits.cpu().numpy())
            all_labels.append(labels.cpu().numpy())
    
    all_logits = np.concatenate(all_logits, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)
    metrics = compute_metrics(all_logits, all_labels, label_names)
    return np.mean(losses), metrics

def main():
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    with mlflow.start_run(run_name=MLFLOW_RUN_NAME) as run:
        print(f"MLflow Run ID: {run.info.run_id}")
        mlflow.log_params({
            "model_name": MODEL_NAME, "train_data": TRAIN_DATA_PATH, "val_data": VAL_DATA_PATH,
            "epochs": EPOCHS, "batch_size": BATCH_SIZE, "learning_rate": LEARNING_RATE,
            "max_seq_length": MAX_LENGTH
        })

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {device}")

        # Load label mapping
        with open(LABEL_MAPPING_PATH, 'r') as f:
            label_map = json.load(f)
        label2id = label_map['label2id']
        id2label = {int(k): v for k,v in label_map['id2label'].items()} # Ensure keys are int for lookup
        NUM_LABELS = len(label2id)
        mlflow.log_param("num_labels", NUM_LABELS)
        mlflow.log_dict(label_map, "label_mapping.json")


        # Load data
        train_df = pd.read_csv(TRAIN_DATA_PATH)
        val_df = pd.read_csv(VAL_DATA_PATH) if os.path.exists(VAL_DATA_PATH) and pd.read_csv(VAL_DATA_PATH).shape[0] > 0 else None

        if train_df.empty:
            print("Training data is empty. Exiting.")
            return

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        train_dataset = IntentDataset(train_df[TEXT_COLUMN].tolist(), train_df[LABEL_COLUMN].tolist(), tokenizer, MAX_LENGTH)
        val_dataset = IntentDataset(val_df[TEXT_COLUMN].tolist(), val_df[LABEL_COLUMN].tolist(), tokenizer, MAX_LENGTH) if val_df is not None else None
        
        train_data_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
        val_data_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE) if val_dataset else None

        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=NUM_LABELS).to(device)

        optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
        total_steps = len(train_data_loader) * EPOCHS
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)
        loss_fn = torch.nn.CrossEntropyLoss().to(device) # For single label classification

        print("\n--- Starting Intent Classifier Training ---")
        best_val_f1 = 0.0
        model_save_path_base = f"saved_models/chatbot/intent_classifier_{MLFLOW_RUN_NAME}"

        for epoch in range(EPOCHS):
            print(f"\nEpoch {epoch + 1}/{EPOCHS}")
            train_loss = train_epoch(model, train_data_loader, loss_fn, optimizer, device, scheduler)
            mlflow.log_metric("train_loss", train_loss, step=epoch)
            print(f"Training Loss: {train_loss:.4f}")

            if val_data_loader:
                print("--- Validating Intent Classifier ---")
                val_loss, val_metrics = eval_model(model, val_data_loader, loss_fn, device, list(id2label.values()))
                mlflow.log_metric("val_loss", val_loss, step=epoch)
                for k, v in val_metrics.items(): mlflow.log_metric(f"val_{k}", v, step=epoch)
                print(f"Validation Loss: {val_loss:.4f}, Val F1 Macro: {val_metrics['f1_macro']:.4f}")

                if val_metrics['f1_macro'] > best_val_f1:
                    best_val_f1 = val_metrics['f1_macro']
                    current_model_save_path = f"{model_save_path_base}_best_epoch{epoch+1}"
                    os.makedirs(current_model_save_path, exist_ok=True)
                    model.save_pretrained(current_model_save_path)
                    tokenizer.save_pretrained(current_model_save_path)
                    print(f"Saved best model to {current_model_save_path}")
                    mlflow.pytorch.log_model(
                        pytorch_model=model,
                        artifact_path="intent_classifier_model",
                        # registered_model_name="ChatbotIntentClassifier", # Optional
                        tokenizer=tokenizer,
                        signature=mlflow.models.infer_signature(
                            tokenizer(train_dataset.texts[0], return_tensors='pt', padding='max_length', truncation=True, max_length=MAX_LENGTH)['input_ids'].cpu().numpy(),
                            model(tokenizer(train_dataset.texts[0], return_tensors='pt', padding='max_length', truncation=True, max_length=MAX_LENGTH)['input_ids'].to(device)).logits.detach().cpu().numpy()
                        )
                    )
        
        print("\n--- Intent Classifier Training Complete ---")
        # Save final model if no validation or if you want the last epoch's model explicitly
        if not val_data_loader or EPOCHS > 0 : # Save last epoch model if no val or if training occurred
            final_model_save_path = f"{model_save_path_base}_final_epoch{EPOCHS}"
            os.makedirs(final_model_save_path, exist_ok=True)
            model.save_pretrained(final_model_save_path)
            tokenizer.save_pretrained(final_model_save_path)
            print(f"Saved final model to {final_model_save_path}")
            if not val_data_loader : # If no val, log this final model as the main one
                 mlflow.pytorch.log_model(pytorch_model=model, artifact_path="intent_classifier_model_final", tokenizer=tokenizer)


        # Conceptual DVC logging
        # print(f"\nTo version with DVC (run manually for best model path):")
        # print(f"dvc add {current_model_save_path_if_best_or_final_model_save_path}")
        # print("git add ... .dvc .gitignore")
        # print("git commit ...")
        # print("dvc push")

if __name__ == "__main__":
    # Ensure data files exist
    if not os.path.exists(TRAIN_DATA_PATH) or not os.path.exists(LABEL_MAPPING_PATH):
        print(f"ERROR: Required data files not found. Run 'prepare_chatbot_intent_data.py' first.")
    else:
        main()