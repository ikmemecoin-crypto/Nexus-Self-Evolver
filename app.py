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
    
    /* Overall Aesthetic */
    html, body, [class*="st-"] {
        font-family: 'Outfit', sans-serif;
        background-color: #1e1f20; /* Sophisticated Gray Background */
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

    /* Modern Tab/Message Style */
    div[data-testid="stChatMessage"] {
        background-color: #282a2c !important; /* Slightly lighter gray tabs */
        border-radius: 20px !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* Fixed Floating Input Bar */
    .stChatInputContainer {
        position: fixed;
        bottom: 30px;
        border-radius: 30px !important;
        border: 1px solid #444746 !important;
        background-color: #282a2c !important;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Clean Sidebar */
    [data-testid="stSidebar"] {
        background-color: #131314 !important; /* Darker Sidebar for contrast */
        border-right: 1px solid #333;
    }

    /* Buttons Style */
    .stButton>button {
        border-radius: 12px;
        background-color: #2d2f31;
        color: white;
        border: 1px solid #444746;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #3c4043;
        border-color: #8e918f;
    }

    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & REPO ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except:
    st.error("📡 AUTH ERROR: Check your Streamlit Secrets.")
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
        st.toast("Memory Synced")

# --- 5. MAIN CHAT INTERFACE ---
st.markdown(f'<h1 class="nexus-header">Hello, {st.session_state.user_name}</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Conversation History
for message in st.session_state.messages:
    avatar = "✨" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# AI PROCESSING LOGIC
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="✨"):
        try:
            ctx = st.session_state.memory_data.get('chat_summary', 'No history.')
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"User: {st.session_state.user_name}. History: {ctx}. Task: {st.session_state.messages[-1]['content']}"
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            if "429" in str(e):
                st.warning("⚡ Nexus is cooling down. Please wait 30 seconds.")
            else:
                st.error(f"Error: {e}")

# PERMANENT ASK TAB
if prompt := st.chat_input("Enter a prompt here"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()
