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
    .stChatMessage { background: rgba(0, 210, 255, 0.05); border-radius: 10px; border-left: 3px solid #00d2ff; }
    .stButton>button { border-radius: 20px; border: 1px solid #00d2ff; background: transparent; color: #00d2ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & GITHUB ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
g = Github(st.secrets["GH_TOKEN"])
repo = g.get_repo(st.secrets["GH_REPO"])

# --- 3. IDENTITY & MEMORY PERSISTENCE ---
if 'user_name' not in st.session_state:
    try:
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
        st.session_state.user_name = st.session_state.memory_data.get("user_name", "Adil")
    except:
        st.session_state.user_name = "Adil"
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧬 NEXUS CORE")
    st.write(f"Commander: **{st.session_state.user_name}**")
    
    # THE MEMORY SAVE BUTTON
    if st.button("💾 Archive Neural Logs"):
        with st.spinner("Writing to GitHub DNA..."):
            # Create a summary of the current session
            history = str(st.session_state.get('messages', []))
            st.session_state.memory_data['chat_summary'] = history[-500:] # Save last 500 chars
            
            # Update GitHub
            content = json.dumps(st.session_state.memory_data)
            f = repo.get_contents("memory.json")
            repo.update_file(f.path, "Archive Chat Memory", content, f.sha)
            st.success("Memory Synced to GitHub!")

# --- 5. CHAT INTERFACE ---
st.title(f"Neural Council: {st.session_state.user_name}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask the Council anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Context: {st.session_state.memory_data.get('chat_summary')}. User {st.session_state.user_name} says: {prompt}"
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
