import streamlit as st
from google import genai
import json
import time
from github import Github

# --- 1. NEXUS-GEMINI GRAY UI ENGINE ---
st.set_page_config(page_title="Nexus", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
    
    /* Global Background Shift to Gray */
    html, body, [class*="st-"] {
        font-family: 'Outfit', sans-serif;
        background-color: #1e1f20; /* Professional Charcoal Gray */
        color: #e3e3e3;
    }

    .main { background-color: #1e1f20; }

    /* Gemini-style Gradient Header */
    .nexus-header {
        font-size: 3rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 20px;
        margin-bottom: 2rem;
    }

    /* Elevated Message Bubbles */
    div[data-testid="stChatMessage"] {
        background-color: #2b2d2f !important; /* Lighter Gray for Chat Tabs */
        border-radius: 24px !important;
        padding: 18px !important;
        margin-bottom: 12px !important;
        border: 1px solid rgba(255,255,255,0.03) !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* Fixed Floating Input Bar */
    .stChatInputContainer {
        position: fixed;
        bottom: 35px;
        border-radius: 32px !important;
        border: 1px solid #444746 !important;
        background-color: #2b2d2f !important;
        z-index: 1000;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Contrast Sidebar */
    [data-testid="stSidebar"] {
        background-color: #131314 !important; /* Deep Dark Sidebar for Contrast */
        border-right: 1px solid #333;
    }

    /* Button Polish */
    .stButton>button {
        border-radius: 14px;
        background-color: #2d2f31;
        color: #e3e3e3;
        border: 1px solid #444746;
        padding: 8px 24px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #3c4043;
        border-color: #8e918f;
        transform: translateY(-1px);
    }

    /* Clean UI Overrides */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & REPO ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except:
    st.error("📡 AUTH ERROR: Connection to Nexus Core Failed.")
    st.stop()

# --- 3. PERSISTENT MEMORY ---
if 'memory_data' not in st.session_state:
    try:
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
    except:
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
    st.session_state.user_name = st.session_state.memory_data.get("user_name", "Adil")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#e3e3e3; font-weight:400; font-family:Outfit;'>Nexus</h1>", unsafe_allow_html=True)
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("💾 Sync Memory", use_container_width=True):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.get('messages', [])])
        st.session_state.memory_data['chat_summary'] = history[-800:]
        content = json.dumps(st.session_state.memory_data)
        f = repo.get_contents("memory.json")
        repo.update_file(f.path, "Update Nexus Memory", content, f.sha)
        st.toast("Nexus DNA Updated")

# --- 5. MAIN CHAT INTERFACE ---
st.markdown(f'<h1 class="nexus-header">Greetings, {st.session_state.user_name}</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Conversation History
for message in st.session_state.messages:
    avatar = "✨" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# AI PROCESSING LOGIC
if len(st.session_state.
