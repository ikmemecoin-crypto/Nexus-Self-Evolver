import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. THE ULTIMATE UI & GLITCH KILLER ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
    
    /* Global Reset */
    html, body, [class*="st-"] { 
        font-family: 'Outfit', sans-serif; 
        background-color: #1e1f20; 
        color: #e3e3e3; 
    }
    
    /* 🚀 THE PERMANENT SIDEBAR FIX: Kills "keyboard_double" and hover glitches */
    [data-testid="collapsedControl"], 
    button[kind="header"], 
    .st-emotion-cache-6qob1r, 
    .st-emotion-cache-10oztos,
    .st-emotion-cache-hp8866 {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Target the sidebar container to ensure it doesn't try to animate/collapse */
    section[data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }

    .main { background-color: #1e1f20; }
    
    .nexus-header {
        font-size: 2.8rem; font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    [data-testid="stSidebar"] { 
        background-color: #131314 !important; 
        border-right: 1px solid #333; 
    }
    
    div[data-testid="stChatMessage"] {
        background-color: #2b2d2f !important; 
        border-radius: 20px !important;
        padding: 15px !important; 
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    .stChatInputContainer { 
        position: fixed; 
        bottom: 35px; 
        border-radius: 32px !important; 
        z-index: 1000; 
    }
    
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE AUTH ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except Exception as e:
    st.error(f"📡 Neural Core Offline: {e}")
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color:#e3e3e3; margin-top:-30px;'>NEXUS OMNI</h2>", unsafe_allow_html=True)
    
    # Live Cooldown Monitor
    if 'cooldown_end' in st.session_state and time.time() < st.session_state.cooldown_end:
        remaining = int(st.session_state.cooldown_end - time.time())
        st.warning(f"⏳ Cooldown: {remaining}s")
        time.sleep(1)
        st.rerun()

    usage_mode = st.radio("Operation Mode", ["Standard Chat", "Live Web Search", "Python Lab"])
    
    st.markdown("---
