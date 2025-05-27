# mental_health_ml/config/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables (call this once, e.g., in main.py or a setup script)
def create_db_and_tables():
    # Import all models here before calling Base.metadata.create_all
    # For example:
    # from mental_health_ml.models.db_models import User, AssessmentResult # etc.
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if they didn't exist).")