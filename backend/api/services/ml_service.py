import joblib
from pathlib import Path
import json
MODEL_PATH = Path(__file__).parent / "predict_model.pkl"
RANGES_PATH = Path(__file__).parent.parent / "utils" / "normal_ranges.json"

def load_model():
    if MODEL_PATH.exists():
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            return None
    return None

def compare_with_ranges(values: dict):
    with open(RANGES_PATH) as f:
        ranges = json.load(f)
    result = {}
    for k,v in values.items():
        if k not in ranges:
            result[k] = {"value": v, "status": "Unknown"}
            continue
        r = ranges[k].get("any", ranges[k].get("male"))
        low, high = r[0], r[1]
        status = "Normal"
        if v < low: 
            status = "Low"
        elif v > high: 
            status = "High"
        result[k] = {
            "value": v, 
            "status": status, 
            "normal_range": r, 
            "unit": ranges[k].get("unit","")
        }
    return result

def predict_risk(values: dict):
    model = load_model()
    features = ["Hemoglobin","WBC","Platelets","Creatinine","SGPT","SGOT","Bilirubin"]
    X = [values.get(f, None) for f in features]
    if model is None or any(x is None for x in X):
        return rule_based(values)
    try:
        pred = model.predict([X])[0]
        prob = None
        if hasattr(model, "predict_proba"):
            prob = max(model.predict_proba([X])[0])
        # Return risks as list of strings and overall risk as string
        risks = [str(pred)] if pred else []
        overall_risk = "High" if prob and prob > 0.7 else "Medium" if prob else "Medium"
        return {"risks": risks, "overall_risk": overall_risk}
    except Exception:
        return rule_based(values)

def rule_based(values: dict):
    risks=[]
    overall="Low"
    hb = values.get("Hemoglobin")
    creat = values.get("Creatinine")
    sgpt = values.get("SGPT")
    sgot = values.get("SGOT")
    if hb is not None and hb < 11:
        risks.append("Anemia_Risk")
    if creat is not None and creat > 1.3:
        risks.append("Kidney_Risk")
    if (sgpt is not None and sgpt>56) or (sgot is not None and sgot>40):
        risks.append("Liver_Risk")
    if len(risks)==0:
        overall="Low"
    elif len(risks)==1:
        overall="Medium"
    else:
        overall="High"
    return {"risks":risks,"overall_risk":overall}
