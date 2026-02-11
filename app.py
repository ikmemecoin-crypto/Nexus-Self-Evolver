import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. GOOGLE MATERIAL DESIGN UI ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Roboto:wght@300;400;500&display=swap');
    
    /* Google Global Styles */
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', 'Roboto', sans-serif; 
        background-color: #131314; 
        color: #e3e3e3; 
    }
    
    .main { background-color: #131314; }

    /* Centered Google-style Header */
    .google-header {
        font-family: 'Google Sans', sans-serif;
        font-size: 3.5rem;
        font-weight: 500;
        text-align: center;
        background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 5vh;
        margin-bottom: 1rem;
    }

    .subtitle {
        text-align: center;
        color: #8e918f;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    /* Material Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #1e1f20 !important; 
        border-right: none;
        padding-top: 2rem;
    }
    
    /* Chat Bubbles (Gemini Style) */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        margin-bottom: 24px !important;
    }

    /* User Message Background */
    div[data-testid="stChatMessage"]:has(img[alt="user"]) > div {
        background-color: #2b2d2f !important;
        border-radius: 28px !important;
        padding: 18px 24px !important;
        max-width: 80%;
        margin-left: auto;
    }
    
    /* Assistant Message Background */
    div[data-testid="stChatMessage"]:has(span:contains("✨")) > div {
        background-color: transparent !important;
        padding: 0 !important;
    }

    /* Floating Search Bar (Google Style) */
    .stChatInputContainer { 
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 32px !important;
        padding: 5px 15px !important;
        margin-bottom: 40px;
    }

    /* Hide UI Clutter */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE AUTH ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except Exception as e:
    st.error("📡 Connection Interrupted. Check API Credentials.")
    st.stop()

# --- 3. GOOGLE SIDEBAR (MATERIAL PILLS) ---
with st.sidebar:
    st.markdown("<h3 style='color:#e3e3e3; padding-left:10px;'>Nexus Omni</h3>", unsafe_allow_html=True)
    
    usage_mode = st.radio("Mode", ["Standard Chat", "Live Web Search", "Python Lab"], label_visibility="collapsed")
    
    st.markdown("<br><p style='color:#8e918f; font-size:0.8rem; padding-left:10px;'>CONTEXT VAULT</p>", unsafe_allow_html=True)
    project_folder = st.selectbox("Project", ["General", "Coding", "Personal", "Research"], label_visibility="collapsed")
    
    # Memory Sync
    memory_filename = f"memory_{project_folder.lower()}.json"
    if 'memory_data' not in st.session_state or st.session_state.get('last_folder') != project_folder:
        try:
            mem_file = repo.get_contents(memory_filename)
            st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
        except:
            st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
        st.session_state.last_folder = project_folder

    st.markdown("---")
    uploaded_img = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    audio_file = st.audio_input("Voice Input")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">How can I help you today, Adil?</div>', unsafe_allow_html=True)

# Feature: Python Lab
if usage_mode == "Python Lab":
    st.markdown("### 🧪 Python Lab")
    with st.form("lab_form"):
        code_input = st.text_area("Code Sandbox", value='print("Hello from Nexus")', height=150)
        run_submitted = st.form_submit_button("Run
