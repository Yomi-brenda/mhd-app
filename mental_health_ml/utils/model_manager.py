# utils/model_manager.py
import torch
import os
import logging
from typing import Dict, Any
import pickle
from datetime import datetime

class ModelManager:
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.loaded_models = {}
        self.model_metadata = {}
        self.logger = logging.getLogger(__name__)
        
    def save_model(self, model, model_name: str, metadata: Dict[str, Any] = None):
        """Save a model with metadata"""
        model_path = os.path.join(self.models_dir, model_name)
        os.makedirs(model_path, exist_ok=True)
        
        # Save model state
        if hasattr(model, 'state_dict'):
            torch.save(model.state_dict(), os.path.join(model_path, "model.pt"))
        else:
            # For sklearn models or other types
            with open(os.path.join(model_path, "model.pkl"), 'wb') as f:
                pickle.dump(model, f)
        
        # Save metadata
        if metadata is None:
            metadata = {}
        metadata['saved_at'] = datetime.now().isoformat()
        metadata['model_type'] = type(model).__name__
        
        with open(os.path.join(model_path, "metadata.json"), 'w') as f:
            import json
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Model {model_name} saved successfully")
        
    def load_model(self, model_class, model_name: str):
        """Load a model from disk"""
        model_path = os.path.join(self.models_dir, model_name)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model {model_name} not found at {model_path}")
        
        # Load metadata
        metadata_path = os.path.join(model_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                import json
                self.model_metadata[model_name] = json.load(f)
        
        # Load model
        pt_path = os.path.join(model_path, "model.pt")
        pkl_path = os.path.join(model_path, "model.pkl")
        
        if os.path.exists(pt_path):
            # PyTorch model
            model = model_class()
            model.load_state_dict(torch.load(pt_path, map_location='cpu'))
            model.eval()
        elif os.path.exists(pkl_path):
            # Pickle model
            with open(pkl_path, 'rb') as f:
                model = pickle.load(f)
        else:
            raise FileNotFoundError(f"No model file found for {model_name}")
        
        self.loaded_models[model_name] = model
        self.logger.info(f"Model {model_name} loaded successfully")
        return model
        
    def get_model_info(self, model_name: str):
        """Get metadata for a model"""
        return self.model_metadata.get(model_name, {})