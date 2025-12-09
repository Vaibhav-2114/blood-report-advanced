import json
from pathlib import Path

HERE = Path(__file__).parent.parent

# Disease diagnosis rules based on blood parameters
DISEASE_RULES = {
    "Anemia": {
        "description": "Low red blood cell count or hemoglobin levels",
        "indicators": [
            {"param": "Hemoglobin", "operator": "<", "value": 11, "weight": 0.9},
            {"param": "WBC", "operator": "<", "value": 4000, "weight": 0.3},
        ],
        "symptoms": ["Fatigue", "Shortness of breath", "Weakness", "Pale skin"]
    },
    "Kidney Disease": {
        "description": "Impaired kidney function",
        "indicators": [
            {"param": "Creatinine", "operator": ">", "value": 1.3, "weight": 0.85},
            {"param": "Bilirubin", "operator": ">", "value": 1.5, "weight": 0.2},
        ],
        "symptoms": ["Fatigue", "Swelling in legs", "Difficulty urinating", "Blood in urine"]
    },
    "Liver Disease": {
        "description": "Impaired liver function",
        "indicators": [
            {"param": "SGPT", "operator": ">", "value": 56, "weight": 0.8},
            {"param": "SGOT", "operator": ">", "value": 40, "weight": 0.8},
            {"param": "Bilirubin", "operator": ">", "value": 1.2, "weight": 0.7},
        ],
        "symptoms": ["Jaundice", "Fatigue", "Abdominal pain", "Dark urine"]
    },
    "Infection/Leukemia": {
        "description": "Bacterial or viral infection, possible blood disorder",
        "indicators": [
            {"param": "WBC", "operator": ">", "value": 11000, "weight": 0.75},
            {"param": "Platelets", "operator": "<", "value": 150000, "weight": 0.6},
        ],
        "symptoms": ["Fever", "Chills", "Easy bruising", "Frequent infections"]
    },
    "Hemolytic Anemia": {
        "description": "Destruction of red blood cells",
        "indicators": [
            {"param": "Hemoglobin", "operator": "<", "value": 10, "weight": 0.85},
            {"param": "Bilirubin", "operator": ">", "value": 2.0, "weight": 0.8},
            {"param": "WBC", "operator": ">", "value": 8000, "weight": 0.4},
        ],
        "symptoms": ["Dark urine", "Yellowing of skin", "Shortness of breath", "Headache"]
    },
    "Thrombocytopenia": {
        "description": "Low platelet count",
        "indicators": [
            {"param": "Platelets", "operator": "<", "value": 150000, "weight": 0.95},
            {"param": "Hemoglobin", "operator": "<", "value": 12, "weight": 0.3},
        ],
        "symptoms": ["Easy bruising", "Petechiae (small red spots)", "Bleeding gums", "Nosebleeds"]
    },
    "Polycythemia": {
        "description": "High red blood cell count",
        "indicators": [
            {"param": "Hemoglobin", "operator": ">", "value": 18, "weight": 0.85},
            {"param": "WBC", "operator": ">", "value": 9000, "weight": 0.4},
        ],
        "symptoms": ["Headache", "Dizziness", "Shortness of breath", "Itching"]
    }
}


def predict_diseases(values: dict):
    """
    Predict possible diseases based on blood report parameters.
    
    Args:
        values: Dictionary of blood test parameters and their values
    
    Returns:
        Dictionary with disease predictions and their confidence scores
    """
    disease_predictions = {}
    
    for disease_name, disease_info in DISEASE_RULES.items():
        confidence_score = 0.0
        matched_indicators = []
        
        for indicator in disease_info["indicators"]:
            param = indicator["param"]
            operator = indicator["operator"]
            threshold = indicator["value"]
            weight = indicator["weight"]
            
            if param not in values:
                continue
            
            param_value = values[param]
            is_match = False
            
            if operator == "<" and param_value < threshold:
                is_match = True
            elif operator == ">" and param_value > threshold:
                is_match = True
            
            if is_match:
                confidence_score += weight
                matched_indicators.append({
                    "parameter": param,
                    "value": param_value,
                    "threshold": threshold,
                    "condition": f"{param} {operator} {threshold}"
                })
        
        # Normalize confidence score (max possible depends on number of indicators)
        max_weight = sum([ind["weight"] for ind in disease_info["indicators"]])
        if max_weight > 0:
            confidence_percentage = min((confidence_score / max_weight) * 100, 100)
        else:
            confidence_percentage = 0
        
        # Only include diseases with at least 30% confidence
        if confidence_percentage >= 30:
            disease_predictions[disease_name] = {
                "confidence": round(confidence_percentage, 1),
                "risk_level": get_risk_level(confidence_percentage),
                "description": disease_info["description"],
                "matched_indicators": matched_indicators,
                "symptoms": disease_info["symptoms"],
                "recommendation": get_recommendation(confidence_percentage)
            }
    
    # Sort by confidence score
    sorted_diseases = dict(sorted(
        disease_predictions.items(),
        key=lambda x: x[1]["confidence"],
        reverse=True
    ))
    
    return {
        "possible_diseases": sorted_diseases,
        "summary": generate_summary(sorted_diseases)
    }


def get_risk_level(confidence: float) -> str:
    """Determine risk level based on confidence score."""
    if confidence >= 80:
        return "High Risk"
    elif confidence >= 60:
        return "Moderate Risk"
    elif confidence >= 40:
        return "Medium Risk"
    else:
        return "Low Risk"


def get_recommendation(confidence: float) -> str:
    """Get medical recommendation based on confidence score."""
    if confidence >= 80:
        return "⚠️ Immediate medical consultation strongly recommended"
    elif confidence >= 60:
        return "⚠️ Medical consultation recommended within a few days"
    elif confidence >= 40:
        return "ℹ️ Consider consulting a healthcare professional"
    else:
        return "ℹ️ Monitor and consult doctor if symptoms appear"


def generate_summary(diseases: dict) -> str:
    """Generate a summary of predicted diseases."""
    if not diseases:
        return "No significant diseases detected based on blood parameters. Regular monitoring recommended."
    
    top_disease = list(diseases.keys())[0]
    top_confidence = diseases[top_disease]["confidence"]
    
    if top_confidence >= 80:
        return f"⚠️ High risk of {top_disease} detected ({top_confidence}% confidence). Immediate medical attention needed."
    elif top_confidence >= 60:
        return f"⚠️ Possible {top_disease} indicated ({top_confidence}% confidence). Medical consultation advised."
    else:
        return f"ℹ️ {top_disease} is a possible condition ({top_confidence}% confidence). Further testing may be needed."
