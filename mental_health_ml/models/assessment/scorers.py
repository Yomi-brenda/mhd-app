# # mental_health_ml/models/assessment/scorers.py
# from typing import List, Dict, Tuple, Optional, Any
# from .questionnaire_configs import get_questionnaire_config

# class StandardizedScorer:
#     def __init__(self, questionnaire_name: str):
#         self.config = get_questionnaire_config(questionnaire_name)
#         if not self.config:
#             raise ValueError(f"No configuration found for questionnaire: {questionnaire_name}")
#         self.questionnaire_name = questionnaire_name

#     def _calculate_sum_score(self, answer_values: List[int]) -> int:
#         """Calculates the sum of answer values."""
#         if len(answer_values) != self.config["questions_count"]:
#             # Handle this case: maybe raise error, or score based on available, or return None
#             # For simplicity now, we'll assume correct number of answers
#             # In a real scenario, you'd need robust handling for missing/partial answers
#             print(f"Warning: Expected {self.config['questions_count']} answers for {self.questionnaire_name}, "
#                   f"got {len(answer_values)}. Scoring based on provided answers.")
#         return sum(answer_values)

#     def _get_category_from_score(self, score: int) -> Optional[str]:
#         """Determines the category based on the score and predefined ranges."""
#         for category, (min_score, max_score) in self.config["scoring_ranges"].items():
#             if min_score <= score <= max_score:
#                 return category
#         return None # Should not happen if ranges are comprehensive

#     def score_assessment(self, responses: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
#         """
#         Scores a list of responses for the configured questionnaire.
#         Each response in the list is expected to be a dict, e.g.,
#         {'question_id': 1, 'answer_value': '2'} or directly {'answer_value': 2}
#         For simplicity, we'll assume 'answer_value' is already numeric or convertible.
#         """
#         if not self.config:
#             return None

#         # Extract numerical answer values, assuming they are ordered correctly
#         # In a real system, you'd map responses to specific questions by question_id or order
#         answer_values: List[int] = []
#         for resp in responses:
#             try:
#                 # Assuming answer_value is directly the score (0, 1, 2, 3)
#                 # and is stored as a string in the DB initially, or already an int
#                 av = resp.get('answer_value')
#                 if isinstance(av, str) and av.isdigit():
#                     answer_values.append(int(av))
#                 elif isinstance(av, (int, float)): # Allow float if that's possible
#                     answer_values.append(int(av))
#                 else:
#                     # Handle non-numeric or missing answer_value for a question
#                     # This could be an error, or you might have a default (e.g., 0)
#                     # or skip scoring if data is incomplete. For now, let's be strict.
#                     print(f"Warning: Invalid or missing answer_value '{av}' for a question in {self.questionnaire_name}.")
#                     # Decide how to handle: skip, default, error.
#                     # For now, if any answer is bad, we might not score.
#                     # A more robust solution would be needed. Let's try to score with what we have or error.
#                     # If we allow partial scoring, the count check in _calculate_sum_score becomes more critical.
#                     # For now, let's assume valid inputs or raise error if not.
#                     # If you want to be lenient, you could append a default (e.g. 0) or skip.
#                     pass # Or raise ValueError(...)
#             except ValueError:
#                 print(f"Warning: Could not convert answer_value '{resp.get('answer_value')}' to int.")
#                 # Decide handling, e.g., skip this response, use default, or fail scoring
#                 pass

#         if len(answer_values) != self.config["questions_count"]:
#              print(f"Error: Insufficient valid answers for {self.questionnaire_name}. "
#                    f"Expected {self.config['questions_count']}, got {len(answer_values)} valid numeric answers.")
#              return {
#                 "predicted_score": None,
#                 "predicted_category": "Incomplete Data",
#                 "confidence": 0.0, # Low confidence due to incomplete data
#                 "interpretation_text": "Assessment could not be scored due to incomplete or invalid answers.",
#                 "raw_model_output": {"error": "Incomplete/invalid data"}
#             }


#         predicted_score = None
#         predicted_category = None

#         if self.config["type"] == "sum_score":
#             predicted_score = self._calculate_sum_score(answer_values)
#             predicted_category = self._get_category_from_score(predicted_score)

#         if predicted_score is not None and predicted_category is not None:
#             # For rule-based, confidence is typically high for the scoring itself.
#             # The clinical validity of the questionnaire is separate.
#             confidence = 1.0
#             interpretation_text = f"Based on the {self.questionnaire_name}, your score of {predicted_score} falls into the '{predicted_category}' range. This is not a diagnosis. Please consult a healthcare professional for further evaluation."

#             return {
#                 "predicted_score": float(predicted_score),
#                 "predicted_category": predicted_category,
#                 "confidence": confidence,
#                 "interpretation_text": interpretation_text,
#                 "raw_model_output": {"answer_values_used": answer_values}
#             }
#         else:
#             return { # Fallback if scoring type is unknown or category not found
#                 "predicted_score": None,
#                 "predicted_category": "Scoring Error",
#                 "confidence": 0.0,
#                 "interpretation_text": "There was an error scoring this assessment.",
#                 "raw_model_output": {"error": "Scoring logic failed or category not found"}
#             }



# mental_health_ml/models/assessment/scorers.py
from .scoring_rules import (
    PHQ9_QUESTIONNAIRE_NAME, PHQ9_SEVERITY_CATEGORIES,
    PHQ9_CRISIS_QUESTION_INDEX, PHQ9_CRISIS_QUESTION_THRESHOLD,
    GAD7_QUESTIONNAIRE_NAME, GAD7_SEVERITY_CATEGORIES,
    INTERPRETATION_TEXTS, RULE_BASED_CONFIDENCE
)

def get_category_from_score(score, category_map):
    """Helper function to find category from a score and a category map."""
    for (low, high), category in category_map.items():
        if low <= score <= high:
            return category
    return "Undefined category" # Should not happen if maps are comprehensive

def score_phq9(answers: list[int]) -> dict:
    """
    Scores PHQ-9 responses.
    Args:
        answers (list[int]): A list of 9 integer scores (0-3).
    Returns:
        dict: Contains total_score, category, crisis_flag, interpretation.
    """
    if len(answers) != 9:
        # Or raise an error, or return an "incomplete" status
        return {
            "predicted_score": None,
            "predicted_category": "Incomplete PHQ-9",
            "confidence": 0.0,
            "crisis_flag_phq9_q9": False,
            "interpretation_text": "PHQ-9 assessment was not fully completed.",
            "raw_model_output": {"error": "Incorrect number of answers for PHQ-9."}
        }

    total_score = sum(answers)
    category = get_category_from_score(total_score, PHQ9_SEVERITY_CATEGORIES)

    crisis_flag_q9 = False
    if answers[PHQ9_CRISIS_QUESTION_INDEX] >= PHQ9_CRISIS_QUESTION_THRESHOLD:
        crisis_flag_q9 = True
        # Potentially override or add to interpretation text
        interpretation = INTERPRETATION_TEXTS[PHQ9_QUESTIONNAIRE_NAME].get(
            "Crisis_Flag_PHQ9",
            "A response has indicated potential crisis. Please seek support."
        )
        # Even if total score is low, crisis flag takes precedence for action
        # For simplicity, we'll keep the score-based category but highlight the flag.
        # Alternatively, category could be "Crisis Indicated"
    else:
        interpretation = INTERPRETATION_TEXTS[PHQ9_QUESTIONNAIRE_NAME].get(category, "No interpretation available.")


    return {
        "predicted_score": float(total_score),
        "predicted_category": category,
        "confidence": RULE_BASED_CONFIDENCE,
        "crisis_flag_phq9_q9": crisis_flag_q9, # Specific flag for PHQ-9 Question 9
        "interpretation_text": interpretation,
        "raw_model_output": {"answers_provided": answers}
    }

def score_gad7(answers: list[int]) -> dict:
    """
    Scores GAD-7 responses.
    Args:
        answers (list[int]): A list of 7 integer scores (0-3).
    Returns:
        dict: Contains total_score, category, interpretation.
    """
    if len(answers) != 7:
        return {
            "predicted_score": None,
            "predicted_category": "Incomplete GAD-7",
            "confidence": 0.0,
            "interpretation_text": "GAD-7 assessment was not fully completed.",
            "raw_model_output": {"error": "Incorrect number of answers for GAD-7."}
        }

    total_score = sum(answers)
    category = get_category_from_score(total_score, GAD7_SEVERITY_CATEGORIES)
    interpretation = INTERPRETATION_TEXTS[GAD7_QUESTIONNAIRE_NAME].get(category, "No interpretation available.")

    return {
        "predicted_score": float(total_score),
        "predicted_category": category,
        "confidence": RULE_BASED_CONFIDENCE,
        # No specific crisis question in GAD-7 standard scoring, but overall severity can imply need for attention
        "interpretation_text": interpretation,
        "raw_model_output": {"answers_provided": answers}
    }

# Main dispatcher function
def get_assessment_score(questionnaire_name: str, answers: list[int]) -> dict:
    """
    Dispatches to the correct scoring function based on questionnaire name.
    Args:
        questionnaire_name (str): The name of the questionnaire.
        answers (list[int]): List of numerical answer values.
    Returns:
        dict: Scoring results.
    """
    if questionnaire_name == PHQ9_QUESTIONNAIRE_NAME:
        return score_phq9(answers)
    elif questionnaire_name == GAD7_QUESTIONNAIRE_NAME:
        return score_gad7(answers)
    # Add elif for other questionnaires
    # elif questionnaire_name == CUSTOM_SCREENER_NAME:
    #     return score_custom_screener(answers)
    else:
        return {
            "predicted_score": None,
            "predicted_category": f"Unsupported questionnaire: {questionnaire_name}",
            "confidence": 0.0,
            "interpretation_text": "Scoring rules for this questionnaire are not implemented.",
            "raw_model_output": {"error": f"No scorer for {questionnaire_name}."}
        }