# mental_health_ml/tests/unit/test_assessment_scorers.py
import pytest
from mental_health_ml.models.assessment.scorers import get_assessment_score
from mental_health_ml.models.assessment.scoring_rules import (
    PHQ9_QUESTIONNAIRE_NAME, GAD7_QUESTIONNAIRE_NAME
)

class TestPHQ9Scoring:
    def test_minimal_depression(self):
        answers = [0, 0, 1, 0, 0, 1, 0, 0, 0] # Score = 2
        result = get_assessment_score(PHQ9_QUESTIONNAIRE_NAME, answers)
        assert result["predicted_score"] == 2.0
        assert result["predicted_category"] == "Minimal depression"
        assert result["crisis_flag_phq9_q9"] is False

    def test_moderate_depression(self):
        answers = [1, 2, 1, 2, 1, 2, 1, 2, 0] # Score = 12
        result = get_assessment_score(PHQ9_QUESTIONNAIRE_NAME, answers)
        assert result["predicted_score"] == 12.0
        assert result["predicted_category"] == "Moderate depression"
        assert result["crisis_flag_phq9_q9"] is False

    def test_severe_depression_with_crisis_flag(self):
        answers = [3, 3, 3, 3, 3, 3, 3, 3, 2] # Score = 26, Q9 = 2
        result = get_assessment_score(PHQ9_QUESTIONNAIRE_NAME, answers)
        assert result["predicted_score"] == 26.0
        assert result["predicted_category"] == "Severe depression"
        assert result["crisis_flag_phq9_q9"] is True
        assert "crisis resources" in result["interpretation_text"].lower()


    def test_low_score_with_crisis_flag(self):
        answers = [0, 0, 0, 0, 0, 0, 0, 0, 1] # Score = 1, Q9 = 1
        result = get_assessment_score(PHQ9_QUESTIONNAIRE_NAME, answers)
        assert result["predicted_score"] == 1.0
        assert result["predicted_category"] == "Minimal depression" # Category based on score
        assert result["crisis_flag_phq9_q9"] is True # But flag is also true
        assert "crisis resources" in result["interpretation_text"].lower()

    def test_incomplete_phq9(self):
        answers = [1, 1, 1] # Too few answers
        result = get_assessment_score(PHQ9_QUESTIONNAIRE_NAME, answers)
        assert result["predicted_score"] is None
        assert result["predicted_category"] == "Incomplete PHQ-9"

class TestGAD7Scoring:
    def test_mild_anxiety(self):
        answers = [1, 1, 0, 1, 2, 0, 0] # Score = 5
        result = get_assessment_score(GAD7_QUESTIONNAIRE_NAME, answers)
        assert result["predicted_score"] == 5.0
        assert result["predicted_category"] == "Mild anxiety"

    def test_severe_anxiety(self):
        answers = [3, 2, 3, 2, 3, 2, 3] # Score = 18
        result = get_assessment_score(GAD7_QUESTIONNAIRE_NAME, answers)
        assert result["predicted_score"] == 18.0
        assert result["predicted_category"] == "Severe anxiety"

    def test_incomplete_gad7(self):
        answers = [1, 1] # Too few answers
        result = get_assessment_score(GAD7_QUESTIONNAIRE_NAME, answers)
        assert result["predicted_score"] is None
        assert result["predicted_category"] == "Incomplete GAD-7"

def test_unsupported_questionnaire():
    answers = [1, 2, 3]
    result = get_assessment_score("UNKNOWN_Q", answers)
    assert result["predicted_score"] is None
    assert "Unsupported questionnaire" in result["predicted_category"]

# Add more test cases for edge conditions, all categories etc.