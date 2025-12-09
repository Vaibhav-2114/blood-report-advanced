import streamlit as st
import requests, json
from PIL import Image
import io
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Blood Report Analyzer",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Advanced AI-powered Blood Report Analysis System\nVersion 1.0"
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-size: 2.5rem;
    }
    
    h2 {
        color: #2c3e50;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    /* Cards styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Status badges */
    .status-normal {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .status-low {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .status-high {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Get API URL
try:
    API_URL = st.secrets.get("api_url", "http://127.0.0.1:8000")
except:
    API_URL = "http://127.0.0.1:8000"

# Title and description
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🏥 Blood Report Analyzer")
    st.markdown("<p style='text-align: center; color: #666;'>Advanced AI-Powered Analysis System</p>", unsafe_allow_html=True)

# Disclaimer
st.warning("""
⚠️ **DISCLAIMER**: This tool provides informational analysis only and is not a substitute for professional medical advice. 
Always consult qualified healthcare professionals for diagnosis and treatment decisions.
""")

# Sidebar for upload
with st.sidebar:
    st.markdown("## 📁 Upload Report")
    st.markdown("---")
    uploaded = st.file_uploader(
        "Upload blood report (image or PDF)",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="Supported formats: PNG, JPG, JPEG, PDF"
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ Instructions")
    st.markdown("""
    1. Upload your blood report image or PDF
    2. Review the extracted text
    3. Edit parameters if needed
    4. Click 'Analyze' for results
    """)

if uploaded:
    bytes_data = uploaded.read()
    
    # Validate file size
    if len(bytes_data) == 0:
        st.error("❌ Error: Uploaded file is empty")
    elif len(bytes_data) > 50 * 1024 * 1024:
        st.error("❌ Error: File size exceeds 50MB limit")
    else:
        # Display preview
        st.markdown("### 📋 Report Preview")
        try:
            img = Image.open(io.BytesIO(bytes_data))
            col1, col2 = st.columns([2, 1])
            with col1:
                st.image(img, width=None)
        except Exception:
            st.info("ℹ️ Preview not available for this file type.")
        
        # Processing
        with st.spinner("🔄 Processing report..."):
            files = {"file": (uploaded.name, bytes_data, uploaded.type)}
            try:
                r = requests.post(f"{API_URL}/upload-report", files=files, timeout=60)
                if r.status_code == 200:
                    data = r.json()
                    
                    # OCR Results
                    with st.expander("📝 Extracted Text (Raw OCR)", expanded=False):
                        st.text_area(
                            "Raw OCR Output",
                            data.get("text", ""),
                            height=200,
                            disabled=True
                        )
                    
                    values = data.get("values", {})
                    
                    # Edit parameters
                    st.markdown("### ✏️ Blood Parameters")
                    st.markdown("Edit the extracted parameters if needed:")
                    
                    edited = {}
                    cols = st.columns(3)
                    
                    for i, (k, v) in enumerate(values.items()):
                        with cols[i % 3]:
                            edited[k] = st.number_input(
                                k,
                                value=float(v),
                                step=0.1,
                                format="%.2f"
                            )
                    
                    # Analyze button
                    if st.button("🔍 Analyze Report", use_container_width=True):
                        # Prepare payload
                        payload = {}
                        for k, val in edited.items():
                            payload[k] = val
                        
                        with st.spinner("🔄 Analyzing results..."):
                            r2 = requests.post(f"{API_URL}/analyze", json=payload, timeout=30)
                            res = r2.json()
                            
                            # Store in session state for display
                            st.session_state.analysis_results = res
                            st.success("✅ Analysis complete!")
                else:
                    st.error(f"❌ Backend error: {r.status_code}")
            except Exception as e:
                st.error(f"❌ Request failed: {str(e)}")

# Display analysis results if available
if 'analysis_results' in st.session_state:
    res = st.session_state.analysis_results
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Parameter Comparison",
        "⚠️ Risk Assessment",
        "🏥 Disease Analysis",
        "📋 Summary"
    ])
    
    # Tab 1: Parameter Comparison
    with tab1:
        st.markdown("### Blood Parameter Analysis")
        comparison = res.get("comparison", {})
        
        if comparison:
            comp_data = []
            for param, info in comparison.items():
                comp_data.append({
                    "Parameter": param,
                    "Value": f"{info.get('value')} {info.get('unit', '')}",
                    "Status": info.get("status"),
                    "Normal Range": f"{info.get('normal_range', ['N/A', 'N/A'])[0]}-{info.get('normal_range', ['N/A', 'N/A'])[1]} {info.get('unit', '')}"
                })
            
            df = pd.DataFrame(comp_data)
            
            # Color the status column
            def color_status(val):
                if val == "Normal":
                    return 'background-color: #d4edda; color: #155724; font-weight: bold'
                elif val == "Low":
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold'
                elif val == "High":
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                else:
                    return 'background-color: #e2e3e5; color: #383d41; font-weight: bold'
            
            styled_df = df.style.applymap(color_status, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("No parameters to display")
    
    # Tab 2: Risk Assessment
    with tab2:
        st.markdown("### Overall Risk Assessment")
        prediction = res.get("prediction", {})
        
        # Overall risk display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            overall_risk = prediction.get("overall_risk", "Unknown")
            risk_color_map = {
                "Low": ("🟢", "#28a745"),
                "Medium": ("🟡", "#ffc107"),
                "High": ("🔴", "#dc3545")
            }
            emoji, color = risk_color_map.get(overall_risk, ("⚫", "#6c757d"))
            
            st.markdown(f"""
            <div style='background: {color}; padding: 2rem; border-radius: 10px; color: white; text-align: center;'>
                <h2>{emoji} {overall_risk}</h2>
                <p>Overall Risk Level</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            risks = prediction.get("risks", [])
            st.markdown(f"""
            <div style='background: #f8f9fa; padding: 2rem; border-radius: 10px; border-left: 4px solid #007bff;'>
                <h3>🔍 Identified Risks</h3>
                {'<br>'.join([f'• {risk}' for risk in risks]) if risks else 'No specific risks identified'}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='background: #e8f5e9; padding: 2rem; border-radius: 10px; border-left: 4px solid #4caf50;'>
                <h3>✅ Status</h3>
                {'Regular monitoring recommended' if overall_risk == 'Low' else 'Medical consultation advised' if overall_risk == 'Medium' else 'Immediate medical attention needed'}
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 3: Disease Analysis
    with tab3:
        st.markdown("### Possible Disease Predictions")
        diseases_result = res.get("diseases", {})
        summary = diseases_result.get("summary", "")
        
        # Summary alert
        if summary:
            if "High risk" in summary or "Immediate" in summary:
                st.error(summary)
            elif "possible" in summary.lower():
                st.warning(summary)
            else:
                st.success(summary)
        
        possible_diseases = diseases_result.get("possible_diseases", {})
        
        if possible_diseases:
            for disease_name, disease_data in possible_diseases.items():
                confidence = disease_data.get('confidence', 0)
                risk_level = disease_data.get('risk_level', 'Unknown')
                
                # Color code based on confidence
                if confidence >= 80:
                    color = "#f8d7da"
                    icon = "🔴"
                elif confidence >= 60:
                    color = "#fff3cd"
                    icon = "🟡"
                else:
                    color = "#d1ecf1"
                    icon = "🔵"
                
                with st.expander(f"{icon} {disease_name} - {confidence}% Confidence", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**📋 Description:** {disease_data.get('description', 'N/A')}")
                        st.markdown(f"**💊 Recommendation:** {disease_data.get('recommendation', 'N/A')}")
                        
                        st.markdown("**🔍 Matched Indicators:**")
                        indicators = disease_data.get('matched_indicators', [])
                        if indicators:
                            for ind in indicators:
                                st.markdown(f"- **{ind['parameter']}**: {ind['value']} ({ind['condition']})")
                        else:
                            st.markdown("- No specific indicators matched")
                        
                        st.markdown("**⚕️ Associated Symptoms:**")
                        symptoms = disease_data.get('symptoms', [])
                        if symptoms:
                            st.markdown(", ".join([f"*{s}*" for s in symptoms]))
                    
                    with col2:
                        st.markdown(f"<div style='text-align: center; padding: 1rem;'><h3>{confidence}%</h3></div>", unsafe_allow_html=True)
                        st.progress(int(confidence) / 100)
                        st.markdown(f"<div style='background: {color}; padding: 0.5rem; border-radius: 5px; text-align: center;'><strong>{risk_level}</strong></div>", unsafe_allow_html=True)
        else:
            st.success("✅ No significant diseases detected. Regular health monitoring is recommended.")
    
    # Tab 4: Summary Report
    with tab4:
        st.markdown("### 📄 Analysis Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Parameters Analyzed")
            comparison = res.get("comparison", {})
            param_count = len(comparison)
            status_counts = {
                "Normal": sum(1 for p in comparison.values() if p.get("status") == "Normal"),
                "Low": sum(1 for p in comparison.values() if p.get("status") == "Low"),
                "High": sum(1 for p in comparison.values() if p.get("status") == "High"),
            }
            
            st.metric("Total Parameters", param_count)
            for status, count in status_counts.items():
                st.metric(f"{status} Values", count)
        
        with col2:
            st.markdown("#### Disease Predictions")
            diseases_result = res.get("diseases", {})
            possible_diseases = diseases_result.get("possible_diseases", {})
            
            st.metric("Possible Diseases Detected", len(possible_diseases))
            
            if possible_diseases:
                top_disease = list(possible_diseases.items())[0]
                st.metric(f"Top Risk: {top_disease[0]}", f"{top_disease[1]['confidence']}%")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 0.9rem;'>Blood Report Analyzer v1.0 | AI-Powered Medical Analysis</p>", unsafe_allow_html=True)

