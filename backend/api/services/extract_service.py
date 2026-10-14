import json
import re
from pathlib import Path

MAPPING_PATH = Path(__file__).parent.parent / "utils" / "mapping.json"
with MAPPING_PATH.open(encoding="utf-8") as file:
    MAPPING = json.load(file)

KEY_MAP = {
    "hemoglobin": "Hemoglobin",
    "wbc": "WBC",
    "platelets": "Platelets",
    "creatinine": "Creatinine",
    "sgpt": "SGPT",
    "sgot": "SGOT",
    "bilirubin": "Bilirubin",
}


def normalize_key(label: str):
    """Map common report labels to the canonical parameter names."""
    normalized = re.sub(r"[^a-z0-9 ]+", " ", label.lower())
    normalized = " ".join(normalized.split())

    for standard, aliases in MAPPING.items():
        for alias in sorted(aliases, key=len, reverse=True):
            alias = alias.lower().strip()
            if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", normalized):
                return KEY_MAP.get(standard, standard.capitalize())
    return None


def extract_key_values(text: str):
    """Extract likely label/value pairs; results should always be checked manually."""
    values = {}
    pattern = re.compile(
        r"([A-Za-z][A-Za-z0-9 /()_-]{0,50}?)\s*(?::|\s{1,})\s*(-?\d+(?:\.\d+)?)"
    )

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = pattern.search(line)
        if not match:
            continue

        key = normalize_key(match.group(1).strip())
        if not key:
            continue

        try:
            values[key] = float(match.group(2))
        except ValueError:
            continue

    return values
