import streamlit as st
import json
from groq import Groq
from github import Github

# --- 1. CORE SYNC ---
@st.cache_resource
def init_nexus():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g_client, r
    except Exception as e:
        st.error(f"Sync Offline: {e}")
        return None, None

client, repo = init_nexus()

# --- 2. FLAT UI DESIGN (NO SIDEBAR) ---
st.set_page_config(page_title="Nexus Omni", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #080808 !important; color: #f0f0f0 !important; }
    
    /* Force Sidebar Hidden */
    [data-testid="stSidebar"] { display: none; }
    .main .block-container { padding-top: 2rem; max-width: 1200px; }

    .hero-text {
        font-size: 3rem; font-weight: 500; text-align: center;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    
    .panel-box { background: #161616; border: 1px solid #333; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    
    /* Pill Input Bar */
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #3c4043 !important; border-radius: 28px !important; }
    
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. TOP SECTION: HEADER & VAULT ---
st.markdown('<div class="hero-text">Nexus Omni</div>', unsafe_allow_html=True)
c_top1, c_top2 = st.columns([2, 8])
with c_top1:
    project = st.selectbox("Active Vault", ["General", "Coding", "Research"])

# --- 4. MAIN BODY: 3-COLUMN CONTROL CENTER ---
col_left, col_mid = st.columns([4, 6])

with col_left:
    st.markdown("### ✍️ Auto-Writer")
    with st.container(border=True):
        fname = st.text_input("New Filename", "script.py")
        code_body = st.text_area("Source Code", height=200)
        if st.button("🚀 Push to GitHub", use_container_width=True):
            try:
                repo.create_file(fname, "Architect Deploy", code_body)
                st.success("Deployed!")
                st.rerun()
            except Exception as e: st.error(e)

    st.markdown("### 📁 File Manager")
    with st.container(border=True):
        try:
            contents = repo.get_contents("")
            for f_item in contents:
                if f_item.type == "file":
                    with st.expander(f"📄 {f_item.name}"):
                        f_code = f_item.decoded_content.decode()
                        new_f_code = st.text_area("Edit", value=f_code, height=100, key=f"ed_{f_item.sha}")
                        c1, c2 = st.columns(2)
                        if c1.button("💾 Save", key=f"sv_{f_item.sha}"):
                            repo.update_file(f_item.path, "Edit", new_f_code, f_item.sha)
                            st.rerun()
                        if c2.button("🗑️ Delete", key=f"dl_{f_item.sha}"):
                            repo.delete_file(f_item.path, "Delete", f_item.sha)
                            st.rerun()
        except: st.info("Loading Repo...")

with col_mid:
    st.markdown("### 💬 Nexus Chat")
    # Chat container with fixed height
    chat_box = st.container(height=500, border=False)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with chat_box:
        for m in st.session_state.messages:
            with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
                st.markdown(m["content"])

    # SUGGESTED CARDS (FUNCTIONAL)
    sc1, sc2, sc3 = st.columns(3)
    suggest_q = None
    if sc1.button("📝 Code Script"): suggest_q = "Write a Python script"
    if sc2.button("🧠 Brainstorm"): suggest_q = "Brainstorm app ideas"
    if sc3.button("🎨 UI Design"): suggest_q = "Improve my UI/UX"

    # INPUT BAR
    u_input = st.chat_input("Command Nexus...")
    query = u_input or suggest_q

# --- 5. EXECUTION LOGIC ---
if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with chat_box:
        with st.chat_message("assistant", avatar="✨"):
            try:
                mem_path = f"memory_{project.lower()}.json"
                try:
                    f_meta = repo.get_contents(mem_path); vault_data = json.loads(f_meta.decoded_content.decode()); sha = f_meta.sha
                except:
                    vault_data, sha = {"history": []}, None

                comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": query}])
                ans = comp.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})

                # Sync Learning
                vault_data["history"].append(query[:50])
                if sha: repo.update_file(mem_path, "Sync", json.dumps(vault_data), sha)
                else: repo.create_file(mem_path, "Init", json.dumps(vault_data))
                st.rerun()
            except Exception as e: st.error(e)
