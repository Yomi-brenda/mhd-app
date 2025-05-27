# mental_health_ml/models/emotion/schemas.py
from pydantic import BaseModel, Field, conlist
from typing import Dict, Optional, List # Added List

class EmotionPredictionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze for emotions.")
    threshold: Optional[float] = Field(0.3, ge=0.0, le=1.0, description="Confidence threshold for an emotion to be included in detected_emotions.")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "I am feeling wonderful and a bit surprised today!",
                "threshold": 0.25
            }
        }

class EmotionPredictionResponse(BaseModel):
    # Changed from dominant_emotion to a list
    detected_emotions: List[str] = Field(..., description="List of emotions detected above the threshold.")
    confidence_scores: Dict[str, float] = Field(..., description="Dictionary of all 28 emotions and their confidence scores from GoEmotions model.")
    model_version_tag: str = Field(..., description="Version tag of the emotion detection model used.")

    class Config:
        json_schema_extra = {
            "example": {
                "detected_emotions": ["joy", "excitement", "surprise"],
                "confidence_scores": {
                    "admiration": 0.1, "amusement": 0.05, "anger": 0.01, "annoyance": 0.02,
                    "approval": 0.15, "caring": 0.03, "confusion": 0.01, "curiosity": 0.2,
                    "desire": 0.05, "disappointment": 0.01, "disapproval": 0.01, "disgust": 0.01,
                    "embarrassment": 0.02, "excitement": 0.85, "fear": 0.03, "gratitude": 0.1,
                    "grief": 0.01, "joy": 0.92, "love": 0.08, "nervousness": 0.04,
                    "optimism": 0.3, "pride": 0.07, "realization": 0.06, "relief": 0.09,
                    "remorse": 0.01, "sadness": 0.02, "surprise": 0.75, "neutral": 0.05
                },
                "model_version_tag": "SamLowe-roberta-base-go_emotions-v1"
            }
        }