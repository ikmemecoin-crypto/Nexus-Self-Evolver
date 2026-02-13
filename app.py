import streamlit as st
import json
import io
from PIL import Image

# --- 1. 5-TIER VERIFIED IMPORTS ---
try:
    from groq import Groq
    from github import Github
except ImportError:
    st.error("Missing Libraries! Please ensure 'requirements.txt' is updated.")
    st.stop()

# --- 2. AUTHENTICATION ---
@st.cache_resource
def init_nexus():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g_client, r
    except Exception as e:
        st.error(f"Nexus Sync Offline: {e}")
        return None, None

client, repo = init_nexus()

# --- 3. UI CONFIG (DARK MATERIAL) ---
st.set_page_config(page_title="Nexus Omni", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #131314; color: #e3e3e3; }
    .google-header { font-size: 3rem; font-weight: 500; text-align: center; background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #3c4043 !important; border-radius: 24px !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (AUTO-WRITER) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Architect Mode</h2>", unsafe_allow_html=True)
    project = st.selectbox("Vault", ["General", "Coding", "Research"])
    
    st.markdown("---")
    st.markdown("### ✍️ Auto-Writer")
    new_filename = st.text_input("File Name", "logic_module.py")
    code_body = st.text_area("Code to Deploy", height=150)
    
    if st.button("🚀 Push to GitHub"):
        try:
            repo.create_file(new_filename, f"Nexus Deploy: {new_filename}", code_body)
            st.success("File written to GitHub!")
        except Exception as e: st.error(f"Write Error: {e}")

# --- 5. THE LEARNING ENGINE (SYNC FIX) ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat Display
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

query = st.chat_input("Command Nexus...")

if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("assistant", avatar="✨"):
        try:
            # 1. GENERATE RESPONSE
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": query}]
            )
            ans = comp.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

            # 2. THE 409 SYNC FIX (Force-Fetch Latest SHA)
            mem_path = f"memory_{project.lower()}.json"
            try:
                current_file = repo.get_contents(mem_path)
                vault_data = json.loads(current_file.decoded_content.decode())
                current_sha = current_file.sha
            except:
                vault_data = {"history": []}
                current_sha = None

            # Update memory history
            if "history" not in vault_data: vault_data["history"] = []
            vault_data["history"].append(query[:100])
            new_payload = json.dumps(vault_data)

            # 3. ATOMIC WRITE
            if current_sha:
                repo.update_file(mem_path, "Nexus Learning Sync", new_payload, current_sha)
            else:
                repo.create_file(mem_path, "Nexus Init", new_payload)

            st.rerun()
        except Exception as e:
            st.error(f"Neural Error: {e}")
