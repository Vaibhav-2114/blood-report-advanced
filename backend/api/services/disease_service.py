"""Transparent rule-score indicators for educational demonstrations.

These heuristics are not clinically validated and must not be used to diagnose
or rule out a medical condition.
"""

DISEASE_RULES = {
    "Anemia indicator": {
        "description": "A low hemoglobin value can be associated with anemia.",
        "indicators": [
            {"param": "Hemoglobin", "operator": "<", "value": 11, "weight": 0.9},
            {"param": "WBC", "operator": "<", "value": 4000, "weight": 0.3},
        ],
        "symptoms": ["Fatigue", "Shortness of breath", "Weakness", "Pale skin"],
    },
    "Kidney-function indicator": {
        "description": "A raised creatinine value can be associated with altered kidney function.",
        "indicators": [
            {"param": "Creatinine", "operator": ">", "value": 1.3, "weight": 0.85},
            {"param": "Bilirubin", "operator": ">", "value": 1.5, "weight": 0.2},
        ],
        "symptoms": ["Fatigue", "Swelling in legs", "Difficulty urinating", "Blood in urine"],
    },
    "Liver-function indicator": {
        "description": "Raised liver enzymes or bilirubin may need clinical review.",
        "indicators": [
            {"param": "SGPT", "operator": ">", "value": 56, "weight": 0.8},
            {"param": "SGOT", "operator": ">", "value": 40, "weight": 0.8},
            {"param": "Bilirubin", "operator": ">", "value": 1.2, "weight": 0.7},
        ],
        "symptoms": ["Jaundice", "Fatigue", "Abdominal pain", "Dark urine"],
    },
    "Blood-count indicator": {
        "description": "An abnormal white-cell count or low platelet count needs interpretation in context.",
        "indicators": [
            {"param": "WBC", "operator": ">", "value": 11000, "weight": 0.75},
            {"param": "Platelets", "operator": "<", "value": 150000, "weight": 0.6},
        ],
        "symptoms": ["Fever", "Chills", "Easy bruising", "Frequent infections"],
    },
    "Red-cell breakdown indicator": {
        "description": "The combination of selected blood-test changes can require further evaluation.",
        "indicators": [
            {"param": "Hemoglobin", "operator": "<", "value": 10, "weight": 0.85},
            {"param": "Bilirubin", "operator": ">", "value": 2.0, "weight": 0.8},
            {"param": "WBC", "operator": ">", "value": 8000, "weight": 0.4},
        ],
        "symptoms": ["Dark urine", "Yellowing of skin", "Shortness of breath", "Headache"],
    },
    "Low-platelet indicator": {
        "description": "A low platelet count can have many causes and needs clinical interpretation.",
        "indicators": [
            {"param": "Platelets", "operator": "<", "value": 150000, "weight": 0.95},
            {"param": "Hemoglobin", "operator": "<", "value": 12, "weight": 0.3},
        ],
        "symptoms": ["Easy bruising", "Small red skin spots", "Bleeding gums", "Nosebleeds"],
    },
    "High-hemoglobin indicator": {
        "description": "A high hemoglobin value can have several causes and needs clinical interpretation.",
        "indicators": [
            {"param": "Hemoglobin", "operator": ">", "value": 18, "weight": 0.85},
            {"param": "WBC", "operator": ">", "value": 9000, "weight": 0.4},
        ],
        "symptoms": ["Headache", "Dizziness", "Shortness of breath", "Itching"],
    },
}


def predict_diseases(values: dict):
    """Return heuristic matches; the score is not a probability."""
    predictions = {}

    for name, info in DISEASE_RULES.items():
        matched = []
        matched_weight = 0.0
        total_weight = sum(item["weight"] for item in info["indicators"])

        for indicator in info["indicators"]:
            parameter = indicator["param"]
            if parameter not in values:
                continue

            value = values[parameter]
            threshold = indicator["value"]
            operator = indicator["operator"]
            is_match = value < threshold if operator == "<" else value > threshold
            if is_match:
                matched_weight += indicator["weight"]
                matched.append({
                    "parameter": parameter,
                    "value": value,
                    "threshold": threshold,
                    "condition": f"{parameter} {operator} {threshold}",
                })

        score = round((matched_weight / total_weight) * 100, 1) if total_weight else 0
        if matched and score >= 30:
            predictions[name] = {
                "confidence": score,
                "risk_level": get_risk_level(score),
                "description": info["description"],
                "matched_indicators": matched,
                "symptoms": info["symptoms"],
                "recommendation": get_recommendation(score),
            }

    sorted_predictions = dict(
        sorted(predictions.items(), key=lambda item: item[1]["confidence"], reverse=True)
    )
    return {
        "possible_diseases": sorted_predictions,
        "summary": generate_summary(sorted_predictions),
        "disclaimer": (
            "Rule scores are educational heuristics, not medical probabilities or diagnoses. "
            "No result from this tool can rule out a condition."
        ),
    }


def get_risk_level(score: float) -> str:
    if score >= 80:
        return "High rule score"
    if score >= 60:
        return "Moderate rule score"
    if score >= 40:
        return "Medium rule score"
    return "Low rule score"


def get_recommendation(score: float) -> str:
    if score >= 80:
        return "Discuss these results promptly with a qualified healthcare professional."
    if score >= 60:
        return "Arrange a review with a qualified healthcare professional."
    return "Review the original report with a qualified healthcare professional if concerned."


def generate_summary(predictions: dict) -> str:
    if not predictions:
        return "No configured rules were triggered. This does not rule out a medical condition."

    top_name, top = next(iter(predictions.items()))
    return (
        f"The strongest configured rule match is {top_name} "
        f"(rule score: {top['confidence']}%). This is not a diagnosis."
    )
