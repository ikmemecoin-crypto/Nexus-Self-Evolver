import streamlit as st
# ... (rest of your imports)

# --- 1. CLEAN NEXUS UI ---
st.set_page_config(page_title="Nexus Omni", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; background-color: #1e1f20; color: #e3e3e3; }
    .main { background-color: #1e1f20; }
    
    /* 🚀 THE FIX: Permanently hide the broken sidebar chevron text */
    button[kind="header"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] .st-emotion-cache-6qob1r {
        display: none !important;
    }
    /* This targets the specific 'keyboard_double' element */
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    .nexus-header {
        font-size: 2.8rem; font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #333; }
    div[data-testid="stChatMessage"] {
        background-color: #2b2d2f !important; border-radius: 20px !important;
        padding: 15px !important; border: 1px solid rgba(255,255,255,0.05) !important;
    }
    .stChatInputContainer { position: fixed; bottom: 35px; border-radius: 32px !important; z-index: 1000; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ... (rest of your code remains the same)
