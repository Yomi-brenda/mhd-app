# mental_health_ml/models/assessment/schemas.py
from pydantic import BaseModel, Field, conlist
from typing import List, Optional, Union, Dict, Any
import uuid # For session_id if it's a UUID

# Input Schema for the Assessment Scoring API
class AssessmentScoreRequest(BaseModel):
    questionnaire_name: str = Field(..., description="Name of the questionnaire (e.g., 'PHQ-9', 'GAD-7')")
    # Assuming answers are numerical scores after user makes selections.
    # conlist ensures the list has items and specifies item type.
    answers: conlist(Union[int, float], min_length=1) = Field(..., description="List of numerical answer values from the questionnaire.")
    session_id: uuid.UUID = Field(..., description="Unique ID for the assessment session being scored.")

    class Config:
        json_schema_extra = {
            "example": {
                "questionnaire_name": "PHQ-9",
                "answers": [0, 1, 2, 0, 1, 3, 1, 0, 1],
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }

# Output Schema for the Assessment Scoring API
class AssessmentScoreResponse(BaseModel):
    session_id: uuid.UUID = Field(..., description="Unique ID for the assessment session scored.")
    questionnaire_name: str = Field(..., description="Name of the questionnaire scored.")
    predicted_score: Optional[float] = Field(None, description="The calculated total score from the assessment.")
    predicted_category: str = Field(..., description="The determined severity category based on the score.")
    confidence: float = Field(..., description="Confidence of the prediction (1.0 for rule-based).")
    interpretation_text: Optional[str] = Field(None, description="A brief interpretation of the score/category.")
    model_version_tag: Optional[str] = Field(None, description="Version tag of the scoring model/rules used.")
    
    # Specific flags or additional outputs can be added here
    crisis_flag_phq9_q9: Optional[bool] = Field(None, description="Flag indicating if PHQ-9 Question 9 suggests potential crisis.")
    
    # For more complex outputs or debugging, raw_model_output can be used
    raw_model_output: Optional[Dict[str, Any]] = Field(None, description="Raw or detailed output from the scoring logic for debugging or further analysis.")


    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "questionnaire_name": "PHQ-9",
                "predicted_score": 9.0,
                "predicted_category": "Mild depression",
                "confidence": 1.0,
                "interpretation_text": "Your responses suggest you may be experiencing mild depressive symptoms...",
                "model_version_tag": "phq9_standard_v1.0_rules",
                "crisis_flag_phq9_q9": False,
                "raw_model_output": {"answers_provided": [1,1,1,1,1,1,1,1,1]}
            }
        }