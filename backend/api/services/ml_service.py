import json
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).with_name("predict_model.pkl")
RANGES_PATH = Path(__file__).parent.parent / "utils" / "normal_ranges.json"
FEATURES = ["Hemoglobin", "WBC", "Platelets", "Creatinine", "SGPT", "SGOT", "Bilirubin"]


def load_model():
    """Load the optional local demo model. Missing or invalid files use rules instead."""
    if not MODEL_PATH.is_file():
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def compare_with_ranges(values: dict):
    with RANGES_PATH.open(encoding="utf-8") as file:
        ranges = json.load(file)

    result = {}
    for key, value in values.items():
        reference = ranges.get(key)
        if not reference:
            result[key] = {"value": value, "status": "Unknown"}
            continue

        limits = reference.get("any")
        if limits is None:
            # Hemoglobin ranges differ by sex; without that context, report both.
            result[key] = {
                "value": value,
                "status": "Context needed",
                "normal_range": {
                    group: reference[group]
                    for group in ("male", "female")
                    if group in reference
                },
                "unit": reference.get("unit", ""),
            }
            continue

        low, high = limits
        status = "Low" if value < low else "High" if value > high else "Normal"
        result[key] = {
            "value": value,
            "status": status,
            "normal_range": limits,
            "unit": reference.get("unit", ""),
        }
    return result


def predict_risk(values: dict):
    """Use the optional synthetic demo model, or transparent rules as a fallback."""
    model = load_model()
    features = [values.get(name) for name in FEATURES]
    if model is None or any(value is None for value in features):
        return rule_based(values)

    try:
        prediction = model.predict([features])[0]
        probabilities = model.predict_proba([features])[0] if hasattr(model, "predict_proba") else None
        confidence = float(max(probabilities)) if probabilities is not None else None
        risk = "High" if confidence is not None and confidence >= 0.8 else (
            "Medium" if confidence is not None and confidence >= 0.6 else "Low"
        )
        label = str(prediction)
        risks = [] if label.lower() == "normal" else [label]
        return {"risks": risks, "overall_risk": risk, "model_confidence": confidence}
    except Exception:
        return rule_based(values)


def rule_based(values: dict):
    risks = []
    if values.get("Hemoglobin") is not None and values["Hemoglobin"] < 11:
        risks.append("Anemia_Risk")
    if values.get("Creatinine") is not None and values["Creatinine"] > 1.3:
        risks.append("Kidney_Risk")
    if (
        values.get("SGPT") is not None and values["SGPT"] > 56
    ) or (
        values.get("SGOT") is not None and values["SGOT"] > 40
    ):
        risks.append("Liver_Risk")

    overall = "Low" if not risks else "Medium" if len(risks) == 1 else "High"
    return {"risks": risks, "overall_risk": overall}
