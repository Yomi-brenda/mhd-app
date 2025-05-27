# inference/recommendation_endpoint.py
from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Dict, Optional

from models.recommendation.model import ResourceRecommender

router = APIRouter()

# Initialize recommender with sample resources (in production, load from database)
sample_resources = [
    {
        "id": "res-001",
        "title": "Understanding Anxiety",
        "description": "Learn about the causes and symptoms of anxiety disorders",
        "type": "article",
        "tags": ["anxiety", "education", "mental health"],
        "popularity": 4.2
    },
    # Add more sample resources
]

recommender = ResourceRecommender()
recommender.load_resources(sample_resources)

class UserProfile(BaseModel):
    needs: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    mental_state: Optional[Dict[str, float]] = None

class RecommendationRequest(BaseModel):
    user_profile: Optional[UserProfile] = None
    user_history: Optional[List[str]] = None
    assessment_results: Optional[Dict[str, float]] = None
    limit: int = 5

class Resource(BaseModel):
    id: str
    title: str
    description: str
    type: str
    tags: List[str]

class RecommendationResponse(BaseModel):
    recommendations: List[Resource]

@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest = Body(...)):
    if request.assessment_results:
        # Prioritize assessment-based recommendations
        recommended_resources = recommender.recommend_for_assessment(
            request.assessment_results, request.limit)
    elif request.user_profile:
        # Fall back to profile-based recommendations
        recommended_resources = recommender.recommend_for_user(
            request.user_profile, request.user_history, request.limit)
    else:
        # Default to generic popular recommendations
        recommended_resources = sorted(sample_resources, 
                                      key=lambda x: x.get('popularity', 0), 
                                      reverse=True)[:request.limit]
    
    return RecommendationResponse(recommendations=recommended_resources)