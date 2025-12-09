import streamlit as st
import requests, json
from PIL import Image
import io

st.set_page_config(page_title="Blood Report Analyzer", layout="wide")
st.title("AI Blood Report Analyzer — Advanced ML Version")

# Get API URL from secrets or use default
try:
    API_URL = st.secrets.get("api_url", "http://127.0.0.1:8000")
except:
    API_URL = "http://127.0.0.1:8000"

st.sidebar.header("Upload")
uploaded = st.sidebar.file_uploader("Upload blood report (image/pdf page)", type=['png','jpg','jpeg','pdf'])
if uploaded:
    bytes_data = uploaded.read()
    
    # Validate file size
    if len(bytes_data) == 0:
        st.error("Error: Uploaded file is empty")
    elif len(bytes_data) > 50 * 1024 * 1024:  # 50MB limit
        st.error("Error: File size exceeds 50MB limit")
    else:
        try:
            img = Image.open(io.BytesIO(bytes_data))
            st.image(img, caption="Uploaded report preview", use_column_width=True)
        except Exception:
            st.warning("Preview not available for this file type.")
        
        with st.spinner("Sending to OCR..."):
            files = {"file": (uploaded.name, bytes_data, uploaded.type)}
            try:
                r = requests.post(f"{API_URL}/upload-report", files=files, timeout=60)
                if r.status_code==200:
                    data = r.json()
                    st.subheader("OCR Extracted Text")
                    st.text_area("Raw OCR", data.get("text",""), height=200)
                    values = data.get("values",{})
                    st.subheader("Detected Parameters (editable)")
                    edited = {}
                    cols = st.columns(3)
                    i=0
                    for k,v in values.items():
                        with cols[i%3]:
                            edited[k] = st.text_input(k, value=str(v))
                        i+=1
                    if st.button("Analyze"):
                        payload = {}
                        for k,val in edited.items():
                            try:
                                payload[k] = float(val)
                            except:
                                pass
                        r2 = requests.post(f"{API_URL}/analyze", json=payload, timeout=30)
                        res = r2.json()
                        st.subheader("Parameter Comparison")
                        # Display comparison results in a formatted table
                        comparison = res.get("comparison", {})
                        if comparison:
                            comp_data = []
                            for param, info in comparison.items():
                                comp_data.append({
                                    "Parameter": param,
                                    "Value": info.get("value"),
                                    "Unit": info.get("unit", ""),
                                    "Status": info.get("status"),
                                    "Normal Range": f"{info.get('normal_range', ['N/A', 'N/A'])[0]}-{info.get('normal_range', ['N/A', 'N/A'])[1]}"
                                })
                            import pandas as pd
                            st.dataframe(pd.DataFrame(comp_data), use_container_width=True)
                        st.subheader("Prediction & Risk Assessment")
                        prediction = res.get("prediction", {})
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Identified Risks:**")
                            risks = prediction.get("risks", [])
                            if risks:
                                for risk in risks:
                                    st.write(f"• {risk}")
                            else:
                                st.write("No risks identified")
                        with col2:
                            overall_risk = prediction.get("overall_risk", "Unknown")
                            risk_color = "🟢" if overall_risk == "Low" else "🟡" if overall_risk == "Medium" else "🔴"
                            st.metric("Overall Risk Level", f"{risk_color} {overall_risk}")
                        
                        # Display Disease Predictions
                        st.subheader("🏥 Possible Diseases")
                        diseases_result = res.get("diseases", {})
                        summary = diseases_result.get("summary", "")
                        
                        if summary:
                            st.info(summary)
                        
                        possible_diseases = diseases_result.get("possible_diseases", {})
                        
                        if possible_diseases:
                            for disease_name, disease_data in possible_diseases.items():
                                with st.expander(f"{disease_name} - {disease_data.get('risk_level', 'Unknown')} ({disease_data.get('confidence', 0)}% confidence)"):
                                    col1, col2 = st.columns([1, 1])
                                    
                                    with col1:
                                        st.write(f"**Description:** {disease_data.get('description', 'N/A')}")
                                        st.write(f"**Recommendation:** {disease_data.get('recommendation', 'N/A')}")
                                    
                                    with col2:
                                        confidence = disease_data.get('confidence', 0)
                                        st.progress(int(confidence) / 100)
                                        st.metric("Confidence", f"{confidence}%")
                                    
                                    st.write("**Matched Indicators:**")
                                    indicators = disease_data.get('matched_indicators', [])
                                    if indicators:
                                        for ind in indicators:
                                            st.write(f"• {ind['parameter']}: {ind['value']} (threshold: {ind['condition']})")
                                    else:
                                        st.write("No specific indicators matched")
                                    
                                    st.write("**Associated Symptoms:**")
                                    symptoms = disease_data.get('symptoms', [])
                                    if symptoms:
                                        st.write(", ".join(symptoms))
                        else:
                            st.success("✅ No significant diseases detected. Regular monitoring recommended.")
                else:
                    st.error("Backend error: "+str(r.status_code))
            except Exception as e:
                st.error("Request failed: "+str(e))

st.info("If OCR misses values, edit them manually before Analyze.")
