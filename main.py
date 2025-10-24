import agreement_comparision
import data_extration
import json
import streamlit as st
import scraping
from notification import send_email_notification, send_slack_notification

# ---------------------------------------
# Page config
# ---------------------------------------
st.set_page_config(
    page_title="GDPR Contract Compliance Checker",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------
# Theme toggle
# ---------------------------------------
theme = st.sidebar.radio("Choose Theme", ["Light 🌞", "Dark 🌙"])

if theme == "Light 🌞":
    bg_color = "#f0f2f6"
    title_color = "#0f4c5c"
    sub_color = "#3282b8"
    button_bg = "#00bcd4"
    button_hover = "#0097a7"
    text_color = "#0f4c5c"
else:
    bg_color = "#1e1e2f"
    title_color = "#ffd166"
    sub_color = "#06d6a0"
    button_bg = "#118ab2"
    button_hover = "#073b4c"
    text_color = "#ffffff"

# ---------------------------------------
# Custom CSS
# ---------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{background-color: {bg_color}; font-family: 'Segoe UI', sans-serif;}}
    h1 {{color: {title_color}; text-align: center; font-weight: 700;}}
    h2, h3 {{color: {sub_color};}}
    .stButton>button:first-child {{
        background-color: {button_bg}; color: white; border-radius: 10px;
        height: 45px; width: 220px; font-size: 16px;
    }}
    .stButton>button:hover {{background-color: {button_hover}; color: white;}}
    .stProgress>div>div>div>div {{background-color: {button_bg};}}
    .css-1d391kg {{color: {text_color};}}
    .css-1lcbmhc p {{color: {text_color};}}
    </style>
    """, unsafe_allow_html=True
)

# ---------------------------------------
# JSON mapping
# ---------------------------------------
AGREEMENT_JSON_MAP = {
    "Data Processing Agreement": "json_files/dpa.json",
    "Joint Controller Agreement": "json_files/jca.json",
    "Controller-to-Controller Agreement": "json_files/c2c.json",
    "Processor-to-Subprocessor Agreement": "json_files/subprocessor.json",
    "Standard Contractual Clauses": "json_files/scc.json"
}

# ---------------------------------------
# Main App
# ---------------------------------------
st.title("🧾 GDPR Contract Compliance Checker")

uploaded_file = st.file_uploader("📤 Upload your Agreement PDF", type=["pdf"])

if uploaded_file:
    try:
        temp_file = "temp_uploaded.pdf"
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.read())

        st.info("🔍 Detecting agreement type...")
        agreement_type = agreement_comparision.document_type(temp_file)
        st.success(f"**Detected Document Type:** {agreement_type}")

        if agreement_type in AGREEMENT_JSON_MAP:
            progress = st.progress(0)

            # Clause extraction
            st.info("📄 Extracting clauses...")
            unseen_data = data_extration.Clause_extraction(temp_file)
            progress.progress(30)
            st.success("✅ Clause extraction completed.")

            # Load template
            st.info("📚 Loading GDPR template...")
            with open(AGREEMENT_JSON_MAP[agreement_type], "r", encoding="utf-8") as f:
                template_data = json.load(f)
            progress.progress(60)

            # Compare
            st.info("⚖️ Comparing extracted clauses...")
            result = agreement_comparision.compare_agreements(unseen_data, template_data)
            progress.progress(100)
            st.success("✅ Comparison complete!")

            # Display
            st.subheader("📊 Comparison Result")
            if isinstance(result, dict):
                st.json(result)
            else:
                st.write(result)

            # Email notification
            email_body = f"Agreement type: {agreement_type}\n\nComparison Result:\n{result}"
            send_email_notification("📄 Agreement Comparison Result", email_body)
            st.success("📩 Comparison result emailed successfully!")

        else:
            st.error("⚠️ This document type is not supported for GDPR compliance.")

    except Exception as e:
        st.error("❌ An error occurred while processing your file.")
        st.code(str(e), language="python")
        send_slack_notification("Error in Document Comparison", f"An exception occurred: {e}")
