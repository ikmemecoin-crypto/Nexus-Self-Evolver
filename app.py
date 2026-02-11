import streamlit as st
from google import genai
import json
from github import Github

# --- 1. NEXUS-GEMINI STYLING ---
st.set_page_config(page_title="Nexus", layout="wide")

st.markdown("""
    <style>
    /* Gemini-inspired Clean Theme */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        background-color: #131314; /* Google's Dark Mode Background */
        color: #e3e3e3;
    }

    .main { background-color: #131314; }

    /* Header Styling */
    .nexus-header {
        font-size: 2.2rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }

    /* Floating Chat Input like Gemini */
    .stChatInputContainer {
        padding-bottom: 30px;
        background-color: transparent !important;
    }
    
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
    }

    /* Sidebar Clean Look */
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #333;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #444746;
        background: transparent;
        color: #c4c7c5;
        font-size: 14px;
        padding: 5px 20px;
    }
    .stButton>button:hover {
        background: #333537;
        border-color: #8e918f;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & GITHUB ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except Exception as e:
    st.error("Auth Error. Check Secrets.")
    st.stop()

# --- 3. IDENTITY ---
if 'memory_data' not in st.session_state:
    try:
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
    except:
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
    st.session_state.user_name = st.session_state.memory_data.get("user_name", "Adil")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#e3e3e3; font-weight:400;'>Nexus</h2>", unsafe_allow_html=True)
    st.write(f"Settings for **{st.session_state.user_name}**")
    if st.button("+ New Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    if st.button("💾 Save to Memory"):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.get('messages', [])])
        st.session_state.memory_data['chat_summary'] = history[-1000:]
        content = json.dumps(st.session_state.memory_data)
        f = repo.get_contents("memory.json")
        repo.update_file(f.path, "Archive", content, f.sha)
        st.toast("Memory Synced")

# --- 5. CHAT INTERFACE ---
st.markdown(f'<h1 class="nexus-header">Hello, {st.session_state.user_name}</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter a prompt here"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="✨"):
        try:
            ctx = st.session_state.memory_data.get('chat_summary', '')
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"User {st.session_state.user_name}. Past: {ctx}. Task: {st.session_state.messages[-1]['content']}"
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            if "429" in str(e):
                st.warning("Nexus is cooling down... wait 30s.")
            else:
                st.error(f"Error: {e}")
