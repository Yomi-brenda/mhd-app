# mental_health_ml/models/assessment/scoring_rules.py

PHQ9_QUESTIONNAIRE_NAME = "PHQ-9" # Or whatever name you use in assessment_questionnaires table
GAD7_QUESTIONNAIRE_NAME = "GAD-7" # Or whatever name you use

PHQ9_SEVERITY_CATEGORIES = {
    (0, 4): "Minimal depression",
    (5, 9): "Mild depression",
    (10, 14): "Moderate depression",
    (15, 19): "Moderately severe depression",
    (20, 27): "Severe depression",
}
# Question 9 index (0-based if answers are a list)
PHQ9_CRISIS_QUESTION_INDEX = 8 # The 9th question
PHQ9_CRISIS_QUESTION_THRESHOLD = 1 # Score of 1 or more is a flag

GAD7_SEVERITY_CATEGORIES = {
    (0, 4): "Minimal anxiety",
    (5, 9): "Mild anxiety",
    (10, 14): "Moderate anxiety",
    (15, 21): "Severe anxiety",
}

# You can add more questionnaires and their rules here
# CUSTOM_SCREENER_NAME = "Custom Initial Screening"
# CUSTOM_SCREENER_SEVERITY_CATEGORIES = { ... }

# Interpretation texts (examples, these should be clinically reviewed)
INTERPRETATION_TEXTS = {
    "PHQ-9": {
        "Minimal depression": "Your responses suggest minimal or no depressive symptoms. Continue to monitor your well-being.",
        "Mild depression": "Your responses suggest you may be experiencing mild depressive symptoms. Consider exploring self-help resources or discussing these feelings if they persist or worsen.",
        "Moderate depression": "Your responses suggest you may be experiencing moderate depressive symptoms. It is advisable to discuss these feelings with a healthcare or mental health professional.",
        "Moderately severe depression": "Your responses suggest moderately severe depressive symptoms. It is strongly recommended to seek consultation with a healthcare or mental health professional.",
        "Severe depression": "Your responses indicate severe depressive symptoms. Please seek help from a healthcare or mental health professional as soon as possible. If you are in crisis, please use the emergency resources provided.",
        "Crisis_Flag_PHQ9": "Your response to question 9 about thoughts of self-harm is a serious concern, regardless of your total score. Please reach out for immediate support using the crisis resources provided."
    },
    "GAD-7": {
        "Minimal anxiety": "Your responses suggest minimal or no anxiety symptoms. Continue to monitor your well-being.",
        "Mild anxiety": "Your responses suggest you may be experiencing mild anxiety symptoms. Consider exploring self-help resources for managing anxiety.",
        "Moderate anxiety": "Your responses suggest you may be experiencing moderate anxiety symptoms. Discussing these with a healthcare or mental health professional could be beneficial.",
        "Severe anxiety": "Your responses indicate severe anxiety symptoms. It is strongly recommended to seek consultation with a healthcare or mental health professional.",
    }
    # ... add interpretations for other questionnaires and categories
}

# Predefined confidence for rule-based scoring
RULE_BASED_CONFIDENCE = 1.0