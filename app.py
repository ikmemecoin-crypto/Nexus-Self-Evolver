import streamlit as st
from google import genai
import json
from github import Github

# --- 1. CORE CONFIG & UNIQUE LOOK ---
st.set_page_config(page_title="NEXUS | OS", layout="wide")

# This CSS makes the app look "Attractive & Unique"
st.markdown("""
    <style>
    .main { background: #0b0e14; color: #ffffff; }
    /* Glassmorphism Top Bar */
    .nav-bar {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(0, 210, 255, 0.2);
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid rgba(0, 210, 255, 0.1); }
    .stButton>button { border-radius: 30px; border: 1px solid #00d2ff; background: transparent; color: #00d2ff; transition: 0.3s; }
    .stButton>button:hover { background: #00d2ff; color: #000; box-shadow: 0 0 15px #00d2ff; }
    </style>
    <div class="nav-bar">
        <h1 style="color: #00d2ff; margin: 0; font-family: 'Courier New'; letter-spacing: 5px;">NEXUS COUNCIL V1.0</h1>
        <p style="color: rgba(0, 210, 255, 0.6); margin: 0;">Neural Link Active // Commander Adil</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. AUTH ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
g = Github(st.secrets["GH_TOKEN"])
repo = g.get_repo(st.secrets["GH_REPO"])

# --- 3. MEMORY ---
if 'memory_data' not in st.session_state:
    try:
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
    except:
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": "System Ready."}
    st.session_state.user_name = st.session_state.memory_data.get("user_name", "Adil")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧬 CORE")
    st.write(f"USER: **{st.session_state.user_name}**")
    if st.button("💾 Archive Logs"):
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.get('messages', [])])
        st.session_state.memory_data['chat_summary'] = history_text[-800:]
        content = json.dumps(st.session_state.memory_data)
        f = repo.get_contents("memory.json")
        repo.update_file(f.path, "Sync", content, f.sha)
        st.toast("DNA Synced to GitHub")

# --- 5. CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Speak to the Nexus..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            ctx = st.session_state.memory_data.get('chat_summary', '')
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"User {st.session_state.user_name}. Past: {ctx}. Now: {st.session_state.messages[-1]['content']}"
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            if "429" in str(e):
                st.warning("⚡ API Cooling Down... Wait 30s.")
                if st.button("🔄 Retry"): st.rerun()
