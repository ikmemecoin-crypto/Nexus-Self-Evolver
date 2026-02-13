import streamlit as st
import json
import io
import base64
from PIL import Image

# --- 1. 5-TIER VERIFIED IMPORTS ---
try:
    from groq import Groq
    from github import Github
except ImportError:
    st.error("Check requirements.txt: groq, PyGithub needed.")
    st.stop()

# --- 2. THE "LEARNING" ENGINE ---
@st.cache_resource
def init_nexus():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g_client, r
    except Exception as e:
        st.error(f"Sync Failed: {e}")
        return None, None

client, repo = init_nexus()

# --- 3. UI CONFIG ---
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

# --- 4. SIDEBAR & MEMORY SYNC ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Nexus Omni</h2>", unsafe_allow_html=True)
    project = st.selectbox("Vault (Learning Focus)", ["General", "Coding", "Research"])
    
    # LOAD MEMORY FROM GITHUB
    mem_path = f"memory_{project.lower()}.json"
    if 'vault' not in st.session_state or st.session_state.get('last_p') != project:
        try:
            f = repo.get_contents(mem_path)
            st.session_state.vault = json.loads(f.decoded_content.decode())
            st.session_state.mem_sha = f.sha # For auto-writing updates
        except:
            st.session_state.vault = {"summary": "New Project Started", "learned_facts": []}
            st.session_state.mem_sha = None
        st.session_state.last_p = project

    aud_in = st.audio_input("Voice")

# --- 5. CHAT & AUTO-LEARNING LOGIC ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
chat_container = st.container(height=400, border=False)
with chat_container:
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
            st.markdown(m["content"])

query = st.chat_input("Command Nexus...")

if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("assistant", avatar="✨"):
        # The AI uses past "Learned Facts" to answer
        context = f"Learned so far: {st.session_state.vault['summary']}"
        
        try:
            # 1. GENERATE RESPONSE
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"Context: {context}"}, 
                          {"role": "user", "content": query}]
            )
            ans = comp.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

            # 2. AUTO-LEARNING (Internal Writing)
            # We update the summary based on the new info
            new_summary = f"{st.session_state.vault['summary']} | User asked about: {query[:50]}"
            st.session_state.vault['summary'] = new_summary[-500:] # Keep it tight
            
            # 3. AUTO-WRITE TO GITHUB (Learning Persists)
            updated_data = json.dumps(st.session_state.vault)
            if st.session_state.mem_sha:
                repo.update_file(mem_path, "Nexus Auto-Learning Sync", updated_data, st.session_state.mem_sha)
            else:
                repo.create_file(mem_path, "Nexus Initial Memory", updated_data)
            
            st.rerun()
        except Exception as e:
            st.error(f"Learning Sync Error: {e}")
