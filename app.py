import streamlit as st
from google import genai
import json
from github import Github

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="NEXUS | COUNCIL", layout="wide")

# Unique Cyber Styling
st.markdown("""
    <style>
    .main { background: #0b0e14; color: #00d2ff; }
    .stChatInput { bottom: 20px; }
    .stChatMessage { background: rgba(0, 210, 255, 0.05); border-radius: 10px; border-left: 3px solid #00d2ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
g = Github(st.secrets["GH_TOKEN"])
repo = g.get_repo(st.secrets["GH_REPO"])

# --- 3. IDENTITY ---
if 'user_name' not in st.session_state:
    try:
        mem = json.loads(repo.get_contents("memory.json").decoded_content.decode())
        st.session_state.user_name = mem.get("user_name", "Adil")
    except:
        st.session_state.user_name = "Adil"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧬 NEXUS CORE")
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 12px; height: 12px; background: #00ff00; border-radius: 50%; box-shadow: 0 0 10px #00ff00;"></div>
            <span style="color: #00ff00; font-weight: bold;">Link: Active</span>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"Commander: **{st.session_state.user_name}**")
    
    if st.button("🚀 Switch to Evolution Mode"):
        st.session_state.mode = "evolve"
        st.rerun()

# --- 5. CHAT INTERFACE (The New Agent) ---
st.title(f"Neural Chat: Hello, {st.session_state.user_name}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Speak to the Nexus Council..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"You are the Nexus AI Council. Address the user as {st.session_state.user_name}. Answer: {prompt}"
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
