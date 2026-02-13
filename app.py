import streamlit as st
import json
import io
from PIL import Image

# --- 1. CORE ENGINE & SYNC ---
try:
    from groq import Groq
    from github import Github
except ImportError:
    st.error("Missing Libraries! Update requirements.txt")
    st.stop()

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

# --- 2. BASE STANDARD LAYOUT + ATTRACTIVE STYLING ---
st.set_page_config(page_title="Nexus", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #080808 !important; color: #f0f0f0 !important; }
    .hero-text {
        font-size: 3.5rem; font-weight: 500;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-top: 1rem;
    }
    [data-testid="stSidebar"] { background-color: #111111 !important; border-right: 1px solid #222 !important; }
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #3c4043 !important; border-radius: 28px !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (MANAGER CONTROLS) ---
with st.sidebar:
    st.markdown("<h2 style='color:#4285F4;'>Nexus Vault</h2>", unsafe_allow_html=True)
    project = st.selectbox("Vault Focus", ["General", "Coding", "Research"])
    
    st.markdown("---")
    tab1, tab2 = st.tabs(["✍️ Writer", "📁 Manager"])
    
    with tab1:
        fname = st.text_input("New File Name", "logic.py")
        code_body = st.text_area("Source Code", height=150)
        if st.button("🚀 Push to GitHub"):
            try:
                repo.create_file(fname, "Architect Deploy", code_body)
                st.success("Deployed!")
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")

    with tab2:
        st.markdown("### Assets")
        try:
            contents = repo.get_contents("")
            for f_item in contents:
                if f_item.type == "file":
                    with st.expander(f"📄 {f_item.name}"):
                        content = f_item.decoded_content.decode()
                        # EDIT LOGIC
                        new_content = st.text_area("Edit Code", value=content, height=100, key=f"edit_{f_item.sha}")
                        if st.button("💾 Update", key=f"up_{f_item.sha}"):
                            repo.update_file(f_item.path, "Nexus Edit", new_content, f_item.sha)
                            st.success("Updated!")
                            st.rerun()
                        # DELETE LOGIC
                        if st.button("🗑️ Delete", key=f"del_{f_item.sha}"):
                            repo.delete_file(f_item.path, "Nexus Delete", f_item.sha)
                            st.warning("Deleted!")
                            st.rerun()
        except: st.warning("Syncing files...")

# --- 4. FRONT PAGE DISPLAY ---
st.markdown('<div class="hero-text">Nexus Omni</div>', unsafe_allow_html=True)

# Functional Suggested Cards
c1, c2, c3, c4 = st.columns(4)
suggested_query = None
with c1: 
    if st.button("📝 Code Script"): suggested_query = "Write a Python script for automation"
with c2: 
    if st.button("🧠 Brainstorm"): suggested_query = "Brainstorm new features for this app"
with c3: 
    if st.button("🎨 UI Design"): suggested_query = "How can I make this UI even more attractive?"
with c4: 
    if st.button("🚀 Deploy App"): suggested_query = "Show me how to deploy this app to a custom domain"

# --- 5. CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

user_input = st.chat_input("How can I help you today, Adil?")
query = user_input or suggested_query

# --- 6. LOGIC & AUTO-LEARNING ---
if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("assistant", avatar="✨"):
        try:
            mem_path = f"memory_{project.lower()}.json"
            try:
                f_meta = repo.get_contents(mem_path); vault = json.loads(f_meta.decoded_content.decode()); sha = f_meta.sha
            except:
                vault, sha = {"history": []}, None

            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": query}])
            ans = comp.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

            if "history" not in vault: vault["history"] = []
            vault["history"].append(query[:60])
            if sha: repo.update_file(mem_path, "Sync", json.dumps(vault), sha)
            else: repo.create_file(mem_path, "Init", json.dumps(vault))
            st.rerun()
        except Exception as e: st.error(f"System Error: {e}")
