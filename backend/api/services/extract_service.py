import re, json
from pathlib import Path
HERE = Path(__file__).parent
with open(HERE.parent / "utils" / "mapping.json") as f:
    MAPPING = json.load(f)

def normalize_key(k: str):
    k = re.sub(r'[^a-z0-9 ]+','',k.lower())
    for std, variants in MAPPING.items():
        for v in variants:
            if v in k:
                # Map to proper key names that match normal_ranges.json
                key_map = {
                    'hemoglobin': 'Hemoglobin',
                    'wbc': 'WBC',
                    'platelets': 'Platelets',
                    'creatinine': 'Creatinine',
                    'sgpt': 'SGPT',
                    'sgot': 'SGOT',
                    'bilirubin': 'Bilirubin'
                }
                return key_map.get(std, std.capitalize())
    return None

def extract_key_values(text: str):
    data = {}
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = re.search(r'([A-Za-z \-\(\)/]+)[:\s]+([0-9]+(?:\.[0-9]+)?)', line)
        if m:
            raw_key = m.group(1).strip()
            raw_val = m.group(2)
            key = normalize_key(raw_key)
            try:
                val = float(raw_val)
            except:
                continue
            if key:
                data[key] = val
    return data
