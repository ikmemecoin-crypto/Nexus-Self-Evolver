import streamlit as st
from google import genai
import json
from github import Github

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="NEXUS | COUNCIL", layout="wide")

# --- 2. AUTH & GITHUB ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except Exception as e:
    st.error(f"📡 Connection Error: {e}")
    st.stop()

# --- 3. IDENTITY & MEMORY PERSISTENCE ---
# Initialize session state BEFORE trying to use it
if 'memory_data' not in st.session_state:
    try:
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
    except:
        # Fallback if file doesn't exist yet
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": "System Initialized."}
    
    st.session_state.user_name = st.session_state.memory_data.get("user_name", "Adil")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧬 NEXUS CORE")
    st.write(f"Commander: **{st.session_state.user_name}**")
    
    if st.button("💾 Archive Neural Logs"):
        with st.spinner("Writing to GitHub DNA..."):
            history = str(st.session_state.get('messages', []))
            # Only save the last 1000 characters to prevent 413 Payload Too Large errors
            st.session_state.memory_data['chat_summary'] = history[-1000:] 
            
            content = json.dumps(st.session_state.memory_data)
            try:
                f = repo.get_contents("memory.json")
                repo.update_file(f.path, "Archive Chat Memory", content, f.sha)
                st.success("Memory Synced!")
            except:
                repo.create_file("memory.json", "Create Memory", content)
                st.success("Memory Created!")

# --- 5. CHAT INTERFACE ---
st.title(f"Neural Council: {st.session_state.user_name}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input with fixed Error Handling
if prompt := st.chat_input("Ask the Council anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Clean context for the model
            clean_context = st.session_state.memory_data.get('chat_summary', 'No previous history.')
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"User: {st.session_state.user_name}. Past Info: {clean_context}. Current Request: {prompt}"
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Neural Glitch: {e}")
