# mental_health_ml/services/assessment_service.py
from sqlalchemy.orm import Session
from mental_health_ml.models.db_models import (
    UserAssessmentSession, UserAssessmentResponse, AssessmentQuestionnaire,
    MLAssessmentPrediction
)
from mental_health_ml.models.assessment.scorers import StandardizedScorer
from mental_health_ml.models.assessment.questionnaire_configs import get_questionnaire_config
from uuid import UUID
from datetime import datetime

class AssessmentService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_responses_for_session(self, session_id: UUID) -> list:
        """Fetches all responses for a given assessment session, ordered correctly."""
        # Assuming AssessmentQuestion has an 'order_in_questionnaire' field
        # and UserAssessmentResponse is linked to AssessmentQuestion.
        # For simplicity now, let's assume responses are fetched and can be ordered
        # or that the scorer expects them in the order they were answered.
        # A more robust way is to join with assessment_questions and order by question_order.
        responses_query = self.db.query(UserAssessmentResponse.answer_value) \
            .filter(UserAssessmentResponse.session_id == session_id) \
            # .join(AssessmentQuestion, UserAssessmentResponse.question_id == AssessmentQuestion.id) # If you have AssessmentQuestion model defined and populated
            # .order_by(AssessmentQuestion.order_in_questionnaire) # And AssessmentQuestion has order_in_questionnaire
            # For now, we'll assume the scorer will handle a list of response dicts
            # or that the order of insertion into user_assessment_responses is reliable (not always true)
            # Let's get them as dicts to match scorer expectation
        
        # A better query if you have AssessmentQuestion with order:
        # responses = self.db.query(UserAssessmentResponse.answer_value, AssessmentQuestion.order_in_questionnaire) \
        #     .join(AssessmentQuestion, UserAssessmentResponse.question_id == AssessmentQuestion.id) \
        #     .filter(UserAssessmentResponse.session_id == session_id) \
        #     .order_by(AssessmentQuestion.order_in_questionnaire) \
        #     .all()
        # formatted_responses = [{"answer_value": r.answer_value} for r in responses]


        # Simpler query for now, assuming order of insertion or that scorer handles it
        # or that the API endpoint will pass responses directly.
        # For this service method, let's assume we need to fetch.
        db_responses = self.db.query(UserAssessmentResponse.answer_value, UserAssessmentResponse.question_id)\
            .filter(UserAssessmentResponse.session_id == session_id)\
            .all() # This doesn't guarantee order unless question_id implies order or you sort later

        # It's better if the caller (e.g., API endpoint) already has the responses
        # in the correct order. For this service, we fetch and assume the scorer can
        # deal with the list. The StandardizedScorer currently expects a list of dicts
        # with 'answer_value'.

        # Let's construct what the scorer expects: a list of dicts, each with 'answer_value'
        # We need to ensure they are in the correct order for questionnaires like PHQ-9.
        # This requires joining with AssessmentQuestion and sorting by its order field.

        # Placeholder for ordered responses - THIS NEEDS TO BE IMPLEMENTED CORRECTLY
        # For now, we'll just get the values. The scorer has a check for count.
        ordered_responses_data = []
        # Example of how you might get ordered responses (if AssessmentQuestion model has 'order_in_questionnaire')
        # from mental_health_ml.models.db_models import AssessmentQuestion # Assuming you have this model
        # query_results = self.db.query(UserAssessmentResponse.answer_value) \
        #     .join(AssessmentQuestion, UserAssessmentResponse.question_id == AssessmentQuestion.id) \
        #     .filter(UserAssessmentResponse.session_id == session_id) \
        #     .order_by(AssessmentQuestion.order_in_questionnaire.asc()) \
        #     .all()
        # ordered_responses_data = [{"answer_value": r.answer_value} for r in query_results]
        # For now, just use the fetched (potentially unordered) responses; scorer will check count.
        # This part is crucial for accuracy and needs careful implementation based on your DB schema.
        
        # Let's assume for the purpose of this service, responses come in as a list of dicts
        # already in order, or the scorer's `responses` argument is handled carefully.
        # The service method below will assume it gets well-formed data or fetches it.

        # To be truly robust, the service should fetch and order:
        from mental_health_ml.models.db_models import AssessmentQuestion # Assuming this exists
        responses_from_db = self.db.query(UserAssessmentResponse)\
            .join(AssessmentQuestion, UserAssessmentResponse.question_id == AssessmentQuestion.id)\
            .filter(UserAssessmentResponse.session_id == session_id)\
            .order_by(AssessmentQuestion.order_in_questionnaire.asc())\
            .all()
        
        return [{"answer_value": r.answer_value} for r in responses_from_db]


    def process_assessment_session(self, session_id: UUID) -> Optional[MLAssessmentPrediction]:
        session = self.db.query(UserAssessmentSession).get(session_id)
        if not session:
            print(f"Error: Session {session_id} not found.")
            return None

        # Check if already processed
        existing_prediction = self.db.query(MLAssessmentPrediction)\
            .filter(MLAssessmentPrediction.session_id == session_id).first()
        if existing_prediction:
            print(f"Info: Session {session_id} already processed. Returning existing prediction.")
            return existing_prediction

        questionnaire = self.db.query(AssessmentQuestionnaire)\
            .filter(AssessmentQuestionnaire.id == session.questionnaire_id).first()
        if not questionnaire:
            print(f"Error: Questionnaire for session {session_id} not found.")
            return None # Or handle error appropriately

        # Check if this questionnaire type has a registered scorer config
        q_config = get_questionnaire_config(questionnaire.name)
        if not q_config:
            print(f"Info: No standardized scorer registered for questionnaire '{questionnaire.name}'. Skipping rule-based scoring.")
            # Here you could potentially call an ML-based scorer if one existed for this type
            return None 

        responses_data = self.get_responses_for_session(session_id)
        if not responses_data or len(responses_data) != q_config.get("questions_count", -1):
            # Scorer will also handle this, but good to check early
            print(f"Error: Insufficient or mismatched responses for session {session_id} and questionnaire {questionnaire.name}.")
            # Create a prediction indicating an error or incomplete data
            error_prediction_data = {
                "session_id": session_id,
                "model_version": f"{questionnaire.name}_rules_v_error", # Generic error version
                "predicted_score": None,
                "predicted_category": "Error: Incomplete Data",
                "confidence": 0.0,
                "interpretation_text": "The assessment could not be scored due to missing or incomplete responses.",
                "prediction_timestamp": datetime.utcnow(),
                "raw_model_output": {"error": "Incomplete or invalid responses fetched for session."}
            }
            db_prediction = MLAssessmentPrediction(**error_prediction_data)
            self.db.add(db_prediction)
            self.db.commit()
            self.db.refresh(db_prediction)
            return db_prediction

        scorer = StandardizedScorer(questionnaire_name=questionnaire.name)
        score_result = scorer.score_assessment(responses_data)

        if score_result:
            prediction_data = {
                "session_id": session_id,
                # Construct a model_version string. For rule-based, it's more about the rule set version.
                "model_version": f"{questionnaire.name}_standard_rules_v1.0", # Example version
                "predicted_score": score_result.get("predicted_score"),
                "predicted_category": score_result.get("predicted_category"),
                "confidence": score_result.get("confidence"),
                "interpretation_text": score_result.get("interpretation_text"),
                "prediction_timestamp": datetime.utcnow(),
                "raw_model_output": score_result.get("raw_model_output")
            }
            db_prediction = MLAssessmentPrediction(**prediction_data)
            self.db.add(db_prediction)
            # Mark session as completed if it wasn't already
            if session.session_status != "completed":
                session.session_status = "completed"
                session.completed_at = datetime.utcnow()
                self.db.add(session)
            self.db.commit()
            self.db.refresh(db_prediction)
            return db_prediction
        else:
            # Handle case where scoring returned None (e.g. critical error in scorer)
            # This is different from the "Incomplete Data" handled by the scorer itself
            print(f"Error: Scoring failed for session {session_id} with questionnaire {questionnaire.name}.")
            # Log an error prediction
            error_prediction_data = {
                "session_id": session_id,
                "model_version": f"{questionnaire.name}_rules_v_scorer_failure",
                "predicted_score": None,
                "predicted_category": "Error: Scoring Failure",
                "confidence": 0.0,
                "interpretation_text": "A system error occurred while scoring this assessment.",
                "prediction_timestamp": datetime.utcnow(),
                "raw_model_output": {"error": "Scorer returned no result."}
            }
            db_prediction = MLAssessmentPrediction(**error_prediction_data)
            self.db.add(db_prediction)
            self.db.commit()
            self.db.refresh(db_prediction)
            return db_prediction