# inference/chatbot_endpoint.py
from fastapi import APIRouter, Body, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

from models.chatbot.model import MentalHealthChatbot
from models.emotion.model import EmotionDetector
from models.crisis.model import CrisisDetector

router = APIRouter()

# Initialize models
chatbot = MentalHealthChatbot()
emotion_detector = EmotionDetector()
crisis_detector = CrisisDetector(threshold=0.7)

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    response: str
    detected_emotion: Optional[dict] = None
    crisis_detected: bool = False
    recommended_resources: Optional[List[dict]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest = Body(...), background_tasks: BackgroundTasks = None):
    user_input = request.message
    
    # Format conversation history
    history_text = ""
    if request.conversation_history:
        for msg in request.conversation_history:
            prefix = "User: " if msg.role == "user" else "Assistant: "
            history_text += prefix + msg.content + "\n"
    
    # Check for crisis signals
    crisis_result = crisis_detector.detect_crisis(user_input)
    
    # Generate response
    response = chatbot.generate_response(user_input, history_text)
    
    # Detect emotion in user message
    emotion_result = emotion_detector.detect_emotion(user_input)
    
    # Get resource recommendations based on detected emotion/content
    recommended_resources = get_resource_recommendations(
        user_input, 
        emotion_result["dominant_emotion"], 
        crisis_result["crisis_detected"]
    )
    
    # If crisis detected, add task to notify emergency team
    if crisis_result["crisis_detected"] and background_tasks:
        background_tasks.add_task(notify_crisis_team, user_input, crisis_result["confidence"])
    
    return ChatResponse(
        response=response,
        detected_emotion=emotion_result,
        crisis_detected=crisis_result["crisis_detected"],
        recommended_resources=recommended_resources
    )

def get_resource_recommendations(message, emotion, is_crisis):
    """Get relevant resources based on user message and detected emotion"""
    resources = []
    
    # Crisis resources
    if is_crisis:
        resources.append({
            "type": "emergency",
            "title": "SOS Suicide Cameroon",
            "description": "Immediate support for emotional distress or suicidal thoughts.",
            "action": "call",
            "action_data": "+237 659 35 35 43"
        })
        resources.append({
            "type": "helpline",
            "title": "Cameroon Red Cross",
            "description": "Humanitarian support and emergency assistance.",
            "action": "call",
            "action_data": "+237 222 22 17 31"
        })
        resources.append({
            "type": "support",
            "title": "Hope for the Abused and Battered",
            "description": "Support for emotional wellness and abuse recovery.",
            "action": "visit",
            "action_data": "https://www.hope4abusedbattered.com"
        })
    
    # Emotion-based resources
    if emotion == "sadness":
        resources.append({
            "type": "article",
            "title": "Understanding and Managing Sadness",
            "description": "Learn techniques to process feelings of sadness",
            "action": "read",
            "action_data": "/resources/articles/managing-sadness"
        })
    
    elif emotion == "anxiety" or emotion == "fear":
        resources.append({
            "type": "exercise",
            "title": "5-Minute Anxiety Relief Exercise",
            "description": "A quick breathing technique for immediate relief",
            "action": "start",
            "action_data": "/resources/exercises/quick-anxiety-relief"
        })
    
    # Add more emotion-based resources
    
    return resources

def notify_crisis_team(message, confidence):
    """Background task to notify crisis response team"""
    # In production, implement actual notification logic
    print(f"[CRISIS CAMEROON] Notify SOS team: '{message}' with confidence {confidence:.2f}")
    # In real implementation: send to crisis API endpoint, notify staff, etc.