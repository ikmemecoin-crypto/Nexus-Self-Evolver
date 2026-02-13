import streamlit as st
import json
import io
from PIL import Image

# --- 1. 5-TIER VERIFIED IMPORTS ---
try:
    from groq import Groq
    from github import Github
except ImportError:
    st.error("Library Missing: Run 'pip install groq PyGithub'")
    st.stop()

# --- 2. THE ARCHITECT ENGINE ---
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

# --- 4. SIDEBAR (LEARNING & WRITING CONTROLS) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Architect Mode</h2>", unsafe_allow_html=True)
    project = st.selectbox("Active Vault", ["General", "Coding", "Research"])
    
    # LOAD MEMORY
    mem_path = f"memory_{project.lower()}.json"
    if 'vault' not in st.session_state or st.session_state.get('active_p') != project:
        try:
            f = repo.get_contents(mem_path)
            st.session_state.vault = json.loads(f.decoded_content.decode())
            st.session_state.mem_sha = f.sha
        except:
            st.session_state.vault = {"summary": "New Project", "code_history": []}
            st.session_state.mem_sha = None
        st.session_state.active_p = project

    st.markdown("---")
    st.markdown("### ✍️ Auto-Writer")
    new_filename = st.text_input("New File Name", "generated_script.py")
    code_to_write = st.text_area("Code to Deploy", height=100)
    
    if st.button("🚀 Push to GitHub"):
        try:
            repo.create_file(new_filename, f"Nexus Auto-Write: {new_filename}", code_to_write)
            st.success(f"Successfully wrote {new_filename} to GitHub!")
        except Exception as e:
            st.error(f"Write Error: {e}")

# --- 5. CHAT & AUTO-LEARNING ENGINE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

chat_container = st.container(height=400, border=False)
with chat_container:
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
            st.markdown(m["content"])

query = st.chat_input("Command Nexus to write or learn...")

if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("assistant", avatar="✨"):
        context = f"Learned context: {st.session_state.vault.get('summary', '')}"
        try:
            # 1. GENERATE
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"You are Nexus Omni. {context}"}, 
                          {"role": "user", "content": query}]
            )
            ans = comp.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

            # 2. AUTO-LEARN (Write back to memory)
            st.session_state.vault['summary'] = f"{st.session_state.vault['summary']} | {query[:30]}"
            updated_data = json.dumps(st.session_state.vault)
            
            if st.session_state.mem_sha:
                repo.update_file(mem_path, "Auto-Learning Sync", updated_data, st.session_state.mem_sha)
            else:
                repo.create_file(mem_path, "Initial Vault", updated_data)
            
            st.rerun()
        except Exception as e:
            st.error(f"Neural Error: {e}")
