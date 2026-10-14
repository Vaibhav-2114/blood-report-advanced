import os
import io

import pandas as pd
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Blood Report Analyzer", page_icon="🩸", layout="wide")
st.title("Blood Report Analyzer")
st.caption("Educational demo only — not for diagnosis or treatment.")

try:
    api_url = st.secrets.get("api_url", os.getenv("API_URL", "http://127.0.0.1:8000"))
except Exception:
    api_url = os.getenv("API_URL", "http://127.0.0.1:8000")

API_URL = api_url.rstrip("/")
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

with st.sidebar:
    st.header("Upload report")
    uploaded = st.file_uploader(
        "Choose a blood report image or PDF",
        type=["png", "jpg", "jpeg", "tif", "tiff", "bmp", "pdf"],
    )
    st.caption("Check all detected values against your original report.")

if uploaded is not None:
    content = uploaded.getvalue()
    if not content:
        st.error("The uploaded file is empty.")
        st.stop()
    if len(content) > MAX_UPLOAD_BYTES:
        st.error("The file is larger than the 50 MB limit.")
        st.stop()

    if uploaded.type and uploaded.type.startswith("image/"):
        try:
            st.image(Image.open(io.BytesIO(content)), caption="Uploaded report", use_container_width=True)
        except Exception:
            st.warning("Image preview is unavailable for this file.")

    if st.button("Extract report values", type="primary"):
        with st.spinner("Extracting text and parameters…"):
            try:
                response = requests.post(
                    f"{API_URL}/upload-report",
                    files={"file": (uploaded.name, content, uploaded.type or "application/octet-stream")},
                    timeout=(10, 120),
                )
                response.raise_for_status()
                data = response.json()
                st.session_state["ocr_text"] = data.get("text", "")
                st.session_state["extracted_values"] = data.get("values", {})
            except requests.RequestException as exc:
                st.error(f"Could not reach the API at {API_URL}: {exc}")
                st.stop()

    if "ocr_text" in st.session_state:
        with st.expander("Extracted text (review carefully)", expanded=False):
            st.text_area("OCR text", st.session_state["ocr_text"], height=200)

        st.subheader("Detected parameters")
        values = st.session_state.get("extracted_values", {})
        if not values:
            st.warning("No supported parameters were detected. Check the extracted text and enter values manually below.")

        editable = {}
        with st.form("analysis_form"):
            for index, (key, value) in enumerate(values.items()):
                editable[key] = st.number_input(key, value=float(value), key=f"value_{key}")
            manual = st.text_input(
                "Additional or missing parameters (optional)",
                help="Enter key=value pairs, e.g. Hemoglobin=13.5, WBC=7000. Canonical names are required.",
            )
            submitted = st.form_submit_button("Analyze values", type="primary")

        if submitted:
            payload = dict(editable)
            if manual.strip():
                for item in manual.split(","):
                    if "=" not in item:
                        continue
                    key, raw_value = item.split("=", 1)
                    try:
                        payload[key.strip()] = float(raw_value.strip())
                    except ValueError:
                        st.warning(f"Skipped invalid number for {key.strip()!r}.")

            if not payload:
                st.error("Enter at least one numeric parameter before analysis.")
                st.stop()

            try:
                response = requests.post(f"{API_URL}/analyze", json=payload, timeout=(10, 45))
                response.raise_for_status()
                result = response.json()
            except requests.RequestException as exc:
                st.error(f"Analysis request failed: {exc}")
                st.stop()

            st.subheader("Reference range comparison")
            comparison = result.get("comparison", {})
            if comparison:
                st.dataframe(
                    pd.DataFrame([
                        {
                            "Parameter": name,
                            "Value": info.get("value"),
                            "Unit": info.get("unit", ""),
                            "Status": info.get("status", "Unknown"),
                            "Reference range": str(info.get("normal_range", "Not available")),
                        }
                        for name, info in comparison.items()
                    ]),
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info("No parameter comparisons were returned.")

            st.subheader("Risk indicators")
            prediction = result.get("prediction", {})
            risk = prediction.get("overall_risk", "Unknown")
            st.metric("Rule/model risk indicator", risk)
            risks = prediction.get("risks", [])
            if risks:
                for item in risks:
                    st.write(f"- {item}")
            else:
                st.write("No configured risk rules were triggered.")

            st.subheader("Rule-based condition indicators")
            diseases = result.get("diseases", {})
            st.info(diseases.get("summary", "No summary was returned."))
            possible = diseases.get("possible_diseases", {})
            if possible:
                for name, details in possible.items():
                    with st.expander(f"{name} — {details.get('risk_level', 'Unknown')}"):
                        st.write(details.get("description", ""))
                        st.write(f"Rule score: {details.get('confidence', 0)}% (not a medical probability)")
                        st.write(details.get("recommendation", ""))
                        st.write("Matched indicators:")
                        indicators = details.get("matched_indicators", [])
                        if indicators:
                            st.table([
                                {
                                    "Parameter": item.get("parameter"),
                                    "Value": item.get("value"),
                                    "Rule": item.get("condition"),
                                }
                                for item in indicators
                            ])
                        symptoms = details.get("symptoms", [])
                        if symptoms:
                            st.write("Associated symptoms listed by the rules: " + ", ".join(symptoms))
            else:
                st.write("No configured condition rules were triggered.")

st.warning(
    "This educational tool can misread reports and uses simplified, non-clinically-validated rules. "
    "Verify every extracted value and consult a qualified healthcare professional. "
    "A displayed score is not a diagnosis or a validated probability."
)
