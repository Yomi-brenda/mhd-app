# inference/assessment_endpoint.py
from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Dict
import torch
from models.assessment.model import MentalHealthAssessmentModel
from data.preprocessing.assessment_preprocessing import AssessmentPreprocessor

router = APIRouter()

# Load model (in production, use a singleton pattern)
model = MentalHealthAssessmentModel()
model.load_state_dict(torch.load("models/assessment/assessment_model.pt"))
model.eval()

preprocessor = AssessmentPreprocessor()

class AssessmentRequest(BaseModel):
    responses: Dict[str, str]

class AssessmentResponse(BaseModel):
    anxiety_level: float
    depression_level: float
    stress_level: float
    wellbeing_score: float
    risk_level: float
    recommendations: List[str]

@router.post("/analyze", response_model=AssessmentResponse)
async def analyze_assessment(request: AssessmentRequest = Body(...)):
    # Convert responses to dataframe format
    responses_text = [f"{q}: {a}" for q, a in request.responses.items()]
    full_text = " ".join(responses_text)
    
    # Preprocess
    inputs = preprocessor.preprocess([full_text])
    
    # Get predictions
    with torch.no_grad():
        outputs = model(inputs["input_ids"], inputs["attention_mask"])
    
    # Convert to response format
    predictions = outputs.numpy()[0]
    
    # Generate recommendations based on predictions
    recommendations = get_recommendations(predictions)
    
    return AssessmentResponse(
        anxiety_level=float(predictions[0]),
        depression_level=float(predictions[1]),
        stress_level=float(predictions[2]),
        wellbeing_score=float(predictions[3]),
        risk_level=float(predictions[4]),
        recommendations=recommendations
    )

def get_recommendations(predictions):
    # Unpack and rescale model outputs to original scale
    anxiety = predictions[0] * 21  # GAD-7 scale
    depression = predictions[1] * 27  # PHQ-9 scale
    stress = predictions[2] * 40  # PSS-10 scale
    wellbeing = predictions[3] * 25  # WHO-5 scale
    risk = predictions[4]  # already 0–1
    
    
    # Logic to generate recommendations based on assessment results
    recommendations = []

    # GAD-7: Anxiety
    if anxiety >= 15:
        recommendations.append("Your anxiety level is severe. Consider professional therapy.")
    elif anxiety >= 10:
        recommendations.append("You may be experiencing moderate anxiety. Mindfulness, meditation, or CBT may help.")
    elif anxiety >= 5:
        recommendations.append("You may have mild anxiety. Practicing relaxation exercises regularly could help.")

    # PHQ-9: Depression
    if depression >= 20:
        recommendations.append("Your depression symptoms are severe. A mental health professional should be consulted.")
    elif depression >= 15:
        recommendations.append("Moderately severe depression symptoms detected. Therapy is strongly recommended.")
    elif depression >= 10:
        recommendations.append("You may be experiencing moderate depression. Talking to a counselor could help.")
    elif depression >= 5:
        recommendations.append("Mild depression detected. Consider tracking mood and staying connected with others.")

    # PSS-10: Stress
    if stress >= 27:
        recommendations.append("High stress level detected. Consider stress management techniques and time off if possible.")
    elif stress >= 14:
        recommendations.append("Moderate stress level. Mindfulness or light exercise may be beneficial.")

    # WHO-5: Wellbeing
    if wellbeing < 13:
        recommendations.append("Low psychological well-being. Prioritize self-care and consider professional help.")
    elif wellbeing < 20:
        recommendations.append("Moderate well-being. Maintain healthy habits and social support.")

    # Overall Risk
    if risk >= 0.8:
        recommendations.append("High overall mental health risk. Immediate evaluation by a mental health professional is advised.")
    elif risk >= 0.5:
        recommendations.append("Moderate risk. Consider a full mental health screening and follow-up.")

    
    return recommendations