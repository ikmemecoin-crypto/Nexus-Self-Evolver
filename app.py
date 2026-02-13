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

# --- 2. PROFESSIONAL STYLING ---
st.set_page_config(page_title="Nexus Omni Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        background-color: #0E1117 !important;
        color: #E0E0E0 !important;
    }
    
    /* Card Styling */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: #1A1C23;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #30363D;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Header Gradient */
    .main-title {
        font-size: 40px;
        font-weight: 600;
        background: linear-gradient(120deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        border: none;
        background: #238636;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #2ea043;
        transform: translateY(-2px);
    }

    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="main-title">Nexus Omni <span style="font-size:15px; color:#8b949e;">Professional v2.0</span></div>', unsafe_allow_html=True)

# --- 4. CONTROL CENTER ---
col_tools, col_chat = st.columns([4, 6], gap="large")

with col_tools:
    st.subheader("✍️ Code Architect")
    with st.container():
        fname = st.text_input("Filename", "main.py", help="Enter name for GitHub")
        code_body = st.text_area("Source Code", height=250, placeholder="# Write logic here...")
        if st.button("🚀 Deploy to Production", use_container_width=True):
            with st.spinner("Pushing to GitHub..."):
                try:
                    repo.create_file(fname, "Pro Deploy", code_body)
                    st.toast("✅ Deployment Successful!", icon='🚀')
                    st.rerun()
                except Exception as e: st.error(f"Push Error: {e}")

    st.markdown("---")
    st.subheader("📁 Repository Manager")
    with st.container():
        try:
            contents = repo.get_contents("")
            for f in contents:
                if f.type == "file":
                    with st.expander(f"📄 {f.name}"):
                        st.code(f.decoded_content.decode()[:200] + "...", language='python')
                        if st.button("Delete File", key=f"del_{f.sha}"):
                            repo.delete_file(f.path, "Delete", f.sha)
                            st.rerun()
        except: st.info("Scanning Repository...")

with col_chat:
    st.subheader("💬 Nexus Intelligent Chat")
    chat_container = st.container(height=550, border=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with chat_container.chat_message(m["role"]):
            st.markdown(m["content"])

    # SUGGESTION PILLS
    cp1, cp2, cp3 = st.columns(3)
    p_input = None
    if cp1.button("🛠️ Fix Bug"): p_input = "Analyze my code for errors."
    if cp2.button("✨ Refactor"): p_input = "Make my UI code more professional."
    if cp3.button("📦 New Feature"): p_input = "Propose a new feature for this app."

    query = st.chat_input("Command the Nexus Architect...") or p_input

if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with chat_container.chat_message("user"):
        st.markdown(query)
    
    with chat_container.chat_message("assistant"):
        with st.spinner("Architecting response..."):
            try:
                # Simple memory check
                mem_path = "memory_general.json"
                try:
                    f_meta = repo.get_contents(mem_path); vault = json.loads(f_meta.decoded_content.decode()); sha = f_meta.sha
                except: vault, sha = {"history": []}, None

                comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": query}])
                ans = comp.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})

                # Record to Vault
                vault["history"].append(query[:50])
                if sha: repo.update_file(mem_path, "Vault Update", json.dumps(vault), sha)
                else: repo.create_file(mem_path, "Vault Init", json.dumps(vault))
            except Exception as e: st.error(e)
