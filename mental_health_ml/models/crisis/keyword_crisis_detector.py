# mental_health_ml/models/crisis/keyword_crisis_detector.py
import re

# --- Keyword Configuration ---
# These lists need to be carefully curated and expanded with clinical input.
# They should be highly indicative of crisis. Consider different categories.
# Using sets for efficient lookup if checking individual words.
# Using regex for phrases allows for more flexibility.

# Category 1: Explicit Suicidal Intent / Self-Harm Methods
# These should be very high-confidence triggers.
# Using \b for word boundaries to avoid matching substrings (e.g., "ass" in "assumption").
SUICIDE_INTENT_PATTERNS = [
    r"\b(kill\s*(my\s*self|myself))\b",
    r"\b(want\s*to\s*die)\b",
    r"\b(end\s*(it\s*all|my\s*life))\b",
    r"\b(suicid(e|al|ing))\b",
    r"\b(no\s*reason\s*to\s*live)\b",
    r"\b(better\s*off\s*dead)\b",
    # Examples of methods (use with extreme caution, these are highly sensitive)
    # r"\b(overdos(e|ing))\b", r"\b(hang\s*(my\s*self|myself))\b", r"\b(jump\s*off\s*a\s*bridge)\b",
    # r"\b(slit\s*my\s*wrists)\b",
    # This list needs to be extremely carefully managed and is illustrative.
    # The goal is to catch unambiguous, direct statements.
]

# Category 2: Severe Hopelessness / Despair (can be precursors or indicative)
HOPELESSNESS_PATTERNS = [
    r"\b(pointless)\b", r"\b(no\s*hope)\b", r"\b(can'?t\s*(take|stand)\s*it\s*anymore)\b",
    r"\b(nothing\s*matters)\b", r"\b(give\s*up)\b",
]

# Category 3: Explicit Self-Harm (Non-Suicidal or method mentions)
SELF_HARM_PATTERNS = [
    r"\b(cut\s*(my\s*self|myself))\b", r"\b(self\s*harm)\b", r"\b(burning\s*myself)\b",
    # Again, specific methods need careful consideration.
]

# It's good practice to have a 'negation' check, but it's hard to make perfect.
# For Layer 1, we might prioritize catching a potential crisis even if it's negated,
# and let Layer 2 or human review sort it out. Or, have simpler negation checks.
# e.g., "i do NOT want to die" - simple negation might miss the "NOT".
# For now, Layer 1 will be aggressive.

# Compile regex patterns for efficiency
COMPILED_SUICIDE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in SUICIDE_INTENT_PATTERNS]
COMPILED_HOPELESSNESS_PATTERNS = [re.compile(p, re.IGNORECASE) for p in HOPELESSNESS_PATTERNS]
COMPILED_SELF_HARM_PATTERNS = [re.compile(p, re.IGNORECASE) for p in SELF_HARM_PATTERNS]


def detect_crisis_keywords(text_input: str) -> dict:
    """
    Scans text for predefined crisis-indicating keywords and patterns.
    Returns:
        dict: {
            "keyword_crisis_detected": bool,
            "matched_category": str or None (e.g., "suicide_intent", "hopelessness"),
            "matched_pattern": str or None (the regex pattern that matched)
        }
    """
    text_lower = text_input.lower() # Normalize for matching

    for pattern in COMPILED_SUICIDE_PATTERNS:
        if pattern.search(text_lower):
            return {
                "keyword_crisis_detected": True,
                "matched_category": "suicide_intent_explicit",
                "matched_pattern": pattern.pattern
            }
    
    for pattern in COMPILED_SELF_HARM_PATTERNS:
        if pattern.search(text_lower):
            return {
                "keyword_crisis_detected": True,
                "matched_category": "self_harm_explicit",
                "matched_pattern": pattern.pattern
            }

    # Hopelessness patterns might be considered slightly less immediate than explicit intent,
    # but still critical to flag.
    for pattern in COMPILED_HOPELESSNESS_PATTERNS:
        if pattern.search(text_lower):
            return {
                "keyword_crisis_detected": True, # Still flag as crisis for Layer 1
                "matched_category": "severe_hopelessness",
                "matched_pattern": pattern.pattern
            }
    
    return {
        "keyword_crisis_detected": False,
        "matched_category": None,
        "matched_pattern": None
    }

if __name__ == "__main__":
    test_texts = [
        "I want to kill myself right now.",
        "I really can't stand it anymore, everything is pointless.",
        "Thinking about cutting myself again.",
        "I'm feeling okay today, no worries.",
        "I would never want to die by suicide.", # Keyword present, but negated (Layer 1 will catch it)
        "He said he wanted to end his life.", # Third person, Layer 1 catches
        "My life has no reason to live for."
    ]

    for text in test_texts:
        result = detect_crisis_keywords(text)
        print(f"Text: \"{text}\"")
        print(f"  Result: {result}\n")