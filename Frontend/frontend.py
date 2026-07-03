import streamlit as st
import requests

# --- CONFIGURATION & EXTERNAL ASSETS ---
API_BASE_URL = "http://127.0.0.1:8000/api"

SYSTEM_LOGO = "https://cdn-icons-png.flaticon.com/512/2966/2966327.png"
DOCTOR_AVATAR = "https://cdn-icons-png.flaticon.com/512/3774/3774299.png" 
AI_AVATAR = "https://cdn-icons-png.flaticon.com/512/2083/2083213.png"     

# FIX 1: Explicitly force the sidebar to always start expanded
st.set_page_config(
    page_title="Clinical Informatics Portal", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS INJECTION ---
st.markdown("""
    <style>
    /* FIX 2: Removed the header hiding rule so we don't break Streamlit's layout engine */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
        border: 1px solid #E2E8F0;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-color: #0A2540;
    }
    
    [data-testid="stFileUploadDropzone"] {
        border-radius: 8px;
        border: 2px dashed #CBD5E1;
        background-color: #F8FAFC;
    }
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None
    
if "last_processed_file" not in st.session_state:
    st.session_state.last_processed_file = None

def start_new_session():
    try:
        response = requests.post(f"{API_BASE_URL}/sessions")
        if response.status_code == 201:
            st.session_state.session_id = response.json()["session_id"]
            st.success(f"System: Patient context #{st.session_state.session_id} initialized.")
    except Exception:
        st.error("System Error: Unable to establish connection to the backend infrastructure.")

# --- UI: SIDEBAR ---
with st.sidebar:
    st.image(SYSTEM_LOGO, width=60)
    st.markdown("### Health Informatics")
    st.markdown("---")
    
    if st.button("Initialize New Patient Context", use_container_width=True):
        start_new_session()
        
    if st.session_state.session_id:
        st.info(f"Active Context ID: {st.session_state.session_id}")

# --- UI: MAIN DASHBOARD INTERFACE ---
st.title("Medical Vision & Diagnostics")
st.markdown("Secure portal for automated POMR clinical summary generation.")
st.markdown("---")

if not st.session_state.session_id:
    st.warning("Action Required: Initialize a patient context via the sidebar to proceed.")
    st.stop()

# 1. Conversation History 
try:
    history_res = requests.get(f"{API_BASE_URL}/sessions/{st.session_state.session_id}/history")
    if history_res.status_code == 200:
        history = history_res.json()["history"]
        for msg in history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar=DOCTOR_AVATAR):
                    st.write(msg["content"])
            elif msg["role"] == "ai":
                with st.chat_message("assistant", avatar=AI_AVATAR):
                    st.write(msg["content"])
except Exception:
    pass 

# 2. Upload Intake 
st.markdown("#### Diagnostic Scan Intake")
uploaded_file = st.file_uploader("Select medical scan (JPEG/PNG)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file is not None:
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    
    if st.session_state.last_processed_file != file_key:
        with st.spinner("Processing visual matrix and generating telemetry..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"symptoms": "Cough and fever for 3 days"}
            res = requests.post(
                f"{API_BASE_URL}/sessions/{st.session_state.session_id}/analyze", 
                files=files,
                data=data
            )
            
            if res.status_code == 200:
                st.toast("Telemetry generated successfully.")
                st.session_state.last_processed_file = file_key
                st.rerun() 
            else:
                st.error(f"Processing Error: {res.json().get('detail', 'Analysis failed')}")