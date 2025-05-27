# mental_health_ml/models/assessment/questionnaire_configs.py

# --- PHQ-9 Configuration ---
PHQ9_NAME = "PHQ-9" # Matches the 'name' in your assessment_questionnaires table
PHQ9_QUESTIONS_COUNT = 9 # Expected number of questions

# Scoring: Typically, options are "Not at all" (0), "Several days" (1),
# "More than half the days" (2), "Nearly every day" (3).
# We assume 'answer_value' in user_assessment_responses stores these numerical scores (0,1,2,3).

PHQ9_SCORING_RANGES = {
    "Minimal depression": (0, 4),
    "Mild depression": (5, 9),
    "Moderate depression": (10, 14),
    "Moderately severe depression": (15, 19),
    "Severe depression": (20, 27),
}

# Question 10 of PHQ-9 is about functional impairment and is scored differently/separately
# For now, we'll focus on the first 9 questions for the main score.

# --- GAD-7 Configuration ---
GAD7_NAME = "GAD-7" # Matches the 'name' in your assessment_questionnaires table
GAD7_QUESTIONS_COUNT = 7

GAD7_SCORING_RANGES = {
    "Minimal anxiety": (0, 4),
    "Mild anxiety": (5, 9),
    "Moderate anxiety": (10, 14),
    "Severe anxiety": (15, 21),
}

# --- General Structure for a Scorer ---
# We'll create a more general processing function later, but these configs help.

REGISTERED_QUESTIONNAIRES = {
    PHQ9_NAME: {
        "questions_count": PHQ9_QUESTIONS_COUNT,
        "scoring_ranges": PHQ9_SCORING_RANGES,
        "type": "sum_score", # Indicates how to calculate the primary score
        # Potentially add specific question IDs if needed, but relying on order is simpler if stable
    },
    GAD7_NAME: {
        "questions_count": GAD7_QUESTIONS_COUNT,
        "scoring_ranges": GAD7_SCORING_RANGES,
        "type": "sum_score",
    },
    # Add other standard questionnaires here
}

def get_questionnaire_config(questionnaire_name: str):
    return REGISTERED_QUESTIONNAIRES.get(questionnaire_name)