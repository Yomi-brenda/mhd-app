# mental_health_ml/models/db_models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid

from mental_health_ml.config.db import Base # Import Base from your db config

class User(Base):
    __tablename__ = "users"
    # Ensure this is UUID and matches the FK in ChatSession
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=True) # Example fields
    email = Column(String, unique=True, nullable=True)    # Example fields
    hashed_password = Column(String, nullable=True)       # Example fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    assessment_sessions = relationship("UserAssessmentSession", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

class AssessmentQuestionnaire(Base):
    __tablename__ = "assessment_questionnaires"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    version = Column(String, default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # questions = relationship("AssessmentQuestion", back_populates="questionnaire")

class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    questionnaire_id = Column(Integer, ForeignKey("assessment_questionnaires.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False) # e.g., "multiple_choice_scale", "free_text"
    options = Column(JSON) # For multiple choice options and their values
    order_in_questionnaire = Column(Integer)
    # questionnaire = relationship("AssessmentQuestionnaire", back_populates="questions")

class UserAssessmentSession(Base):
    __tablename__ = "user_assessment_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Nullable for anonymous
    questionnaire_id = Column(Integer, ForeignKey("assessment_questionnaires.id"), nullable=False)
    session_status = Column(String, default="started") # "started", "in_progress", "completed"
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    # user = relationship("User", back_populates="assessment_sessions")
    # responses = relationship("UserAssessmentResponse", back_populates="session")
    # prediction = relationship("MLAssessmentPrediction", uselist=False, back_populates="session")


class UserAssessmentResponse(Base):
    __tablename__ = "user_assessment_responses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_assessment_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("assessment_questions.id"), nullable=False)
    answer_value = Column(String) # For scaled/choice answers
    answer_text = Column(Text) # For free-text answers
    response_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # session = relationship("UserAssessmentSession", back_populates="responses")
    # question = relationship("AssessmentQuestion")


class MLAssessmentPrediction(Base):
    __tablename__ = "ml_assessment_predictions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_assessment_sessions.id"), unique=True, nullable=False)
    model_version = Column(String)
    predicted_score = Column(Float)
    predicted_category = Column(String)
    confidence = Column(Float)
    interpretation_text = Column(Text)
    prediction_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    raw_model_output = Column(JSON) # Store probabilities or other details
    # session = relationship("UserAssessmentSession", back_populates="prediction")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # FK to users.id
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    session_metadata = Column(JSON)
    # user = relationship("User", back_populates="chat_sessions")
    # messages = relationship("ChatMessage", back_populates="session", order_by="ChatMessage.timestamp")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    sender_type = Column(String, nullable=False) # "user" or "bot"
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    language_code = Column(String, default="en") # Default to English
    # session = relationship("ChatSession", back_populates="messages")
    # emotion_prediction = relationship("MLEmotionPrediction", uselist=False, back_populates="chat_message")
    # crisis_prediction = relationship("MLCrisisPrediction", uselist=False, back_populates="chat_message")


class MLEmotionPrediction(Base):
    __tablename__ = "ml_emotion_predictions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id"), unique=True, nullable=False)
    model_version = Column(String)
    detected_emotion = Column(String)
    confidence_scores = Column(JSON) # {"joy": 0.1, "sadness": 0.7, ...}
    prediction_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # chat_message = relationship("ChatMessage", back_populates="emotion_prediction")


class MLCrisisPrediction(Base):
    __tablename__ = "ml_crisis_predictions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Link to either a specific message or an entire session if crisis is determined from context
    chat_message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id"), nullable=True)
    chat_session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=True) # if session-level analysis
    model_version = Column(String)
    is_crisis_detected = Column(Boolean, default=False)
    crisis_type = Column(String, nullable=True) # e.g., "suicidal_ideation", "self_harm"
    confidence = Column(Float)
    triggering_text_segment = Column(Text, nullable=True)
    prediction_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    action_taken = Column(String, nullable=True) # Log action taken by system or human
    # chat_message = relationship("ChatMessage", back_populates="crisis_prediction")
    # chat_session = relationship("ChatSession") # Add back_populates if needed


class ResourcesContent(Base):
    __tablename__ = "resources_content"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(String) # "article", "video", "exercise", "tool"
    url = Column(String)
    content_body = Column(Text) # If self-hosted
    tags = Column(ARRAY(String)) # Use ARRAY for PostgreSQL native array
    target_conditions = Column(ARRAY(String))
    source = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # For pgvector, you might use a specific type: from pgvector.sqlalchemy import Vector
    # embedding_vector = Column(Vector(dim_size)) # dim_size e.g. 768 for BERT


class UserResourceInteraction(Base):
    __tablename__ = "user_resource_interactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources_content.id"), nullable=False)
    interaction_type = Column(String) # "viewed", "clicked", "saved", "rated_helpful"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    session_id = Column(UUID(as_uuid=True), nullable=True) # Context (chat or assessment session)
    rating = Column(Integer, nullable=True) # e.g., 1-5
    # user = relationship("User")
    # resource = relationship("ResourcesContent")

class MLModelVersion(Base):
    __tablename__ = "ml_model_versions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String, nullable=False, index=True) # "assessment_classifier", "emotion_detector"
    version_tag = Column(String, unique=True, nullable=False) # "v1.0.0-bert-base"
    description = Column(Text)
    mlflow_run_id = Column(String)
    dvc_path_to_model = Column(String) # Path within DVC remote
    deployment_status = Column(String, default="development") # "development", "staging", "production", "archived"
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())