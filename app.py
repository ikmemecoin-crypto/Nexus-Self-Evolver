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
    st.error(f"📡 Auth Error: {e}")
    st.stop()

# --- 3. IDENTITY & MEMORY PERSISTENCE ---
if 'memory_data' not in st.session_state:
    try:
        # Pull from GitHub
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
    except:
        # Default if GitHub is empty
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": "Initial sync."}
    
    st.session_state.user_name = st.session_state.memory_data.get("user_name", "Adil")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧬 NEXUS CORE")
    st.write(f"Commander: **{st.session_state.user_name}**")
    
    if st.button("💾 Archive Neural Logs"):
        with st.spinner("Archiving..."):
            # Cleanly format the history for the save file
            history_text = ""
            if "messages" in st.session_state:
                for m in st.session_state.messages:
                    history_text += f"{m['role']}: {m['content']}\n"
            
            st.session_state.memory_data['chat_summary'] = history_text[-1000:]
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

# Chat Input
if prompt := st.chat_input("Ask the Council anything..."):
    # Add user message to UI immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun() # Refresh to show user bubble before AI thinks

# AI Response Generation (triggered after rerun)
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            context = st.session_state.memory_data.get('chat_summary', 'No history.')
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"User: {st.session_state.user_name}. Summary: {context}. Question: {st.session_state.messages[-1]['content']}"
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Brain Glitch: {e}")
