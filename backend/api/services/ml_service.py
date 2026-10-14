import json
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).with_name("predict_model.pkl")
RANGES_PATH = Path(__file__).parent.parent / "utils" / "normal_ranges.json"
FEATURES = ["Hemoglobin", "WBC", "Platelets", "Creatinine", "SGPT", "SGOT", "Bilirubin"]


def load_model():
    """Load the optional local demo model; use rules if it is absent or invalid."""
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
            # Hemoglobin ranges differ by sex. Do not silently select one range.
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
    """Return a demo label, not a medical prediction."""
    model = load_model()
    features = [values.get(name) for name in FEATURES]
    if model is None or any(value is None for value in features):
        return rule_based(values)

    try:
        label = str(model.predict([features])[0])
        probabilities = model.predict_proba([features])[0] if hasattr(model, "predict_proba") else None
        model_confidence = float(max(probabilities)) if probabilities is not None else None

        # Confidence is confidence in a synthetic demo label, not severity or clinical risk.
        is_normal = label.strip().lower() in {"normal", "healthy", "none"}
        return {
            "risks": [] if is_normal else [label],
            "overall_risk": "Low" if is_normal else "Review",
            "model_confidence": model_confidence,
            "disclaimer": "Experimental output from synthetic training data; not clinically validated.",
        }
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

    overall = "Low" if not risks else "Review"
    return {
        "risks": risks,
        "overall_risk": overall,
        "disclaimer": "Simple thresholds only; not a diagnosis or a clinically validated risk estimate.",
    }
