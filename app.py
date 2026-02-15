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

# --- 2. THEME & PROFESSIONAL STYLING ---
st.set_page_config(page_title="Nexus Pro", layout="wide", initial_sidebar_state="collapsed")

# Theme Selection
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

# CSS Variables based on Theme
if st.session_state.theme_mode == "Dark":
    bg, card, text, accent = "#0E1117", "#1A1C23", "#E0E0E0", "#58a6ff"
else:
    bg, card, text, accent = "#F0F2F6", "#FFFFFF", "#1E1E1E", "#007BFF"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    
    /* Professional Card Glassmorphism */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: {card}; border-radius: 16px; padding: 24px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    }}

    .main-title {{
        font-size: 36px; font-weight: 600;
        background: linear-gradient(120deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    
    [data-testid="stSidebar"] {{ display: none; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. PROFESSIONAL HEADER ---
c_head1, c_head2 = st.columns([8, 2])
with c_head1:
    st.markdown('<div class="main-title">Nexus Omni <span style="font-size:14px; color:gray;">v2.1 Pro</span></div>', unsafe_allow_html=True)
with c_head2:
    st.session_state.theme_mode = st.selectbox("Appearance", ["Dark", "Light"], label_visibility="collapsed")

# --- 4. THE CONTROL CENTER ---
col_writer, col_chat = st.columns([4, 6], gap="large")

with col_writer:
    st.subheader("✍️ Code Architect")
    with st.container():
        fname = st.text_input("Filename", value="new_logic.py", help="Name your file for GitHub")
        code_body = st.text_area("Source Code", height=300, placeholder="# Enter your logic here...")
        if st.button("🚀 Push to Production", use_container_width=True):
            with st.spinner("Syncing with Vault..."):
                try:
                    # Check if exists to avoid 422 error
                    try:
                        f = repo.get_contents(fname)
                        repo.update_file(fname, "Architect Update", code_body, f.sha)
                    except:
                        repo.create_file(fname, "Architect Deploy", code_body)
                    st.toast("Deployment Successful!", icon='✅')
                    st.rerun()
                except Exception as e: st.error(e)

    st.markdown("---")
    st.subheader("📁 Repository Vault")
    with st.container():
        try:
            files = repo.get_contents("")
            for f in files:
                if f.type == "file":
                    with st.expander(f"📄 {f.name}"):
                        st.code(f.decoded_content.decode()[:150] + "...", language='python')
                        if st.button("Delete", key=f"del_{f.sha}"):
                            repo.delete_file(f.path, "Remove", f.sha)
                            st.rerun()
        except: st.info("Scanning...")

with col_chat:
    st.subheader("💬 Nexus Intelligent Chat")
    chat_box = st.container(height=580, border=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with chat_box.chat_message(m["role"]):
            st.markdown(m["content"])

    # PRO SUGGESTIONS
    s1, s2, s3 = st.columns(3)
    p_cmd = None
    if s1.button("🔍 Audit Code"): p_cmd = "Review my latest GitHub file for security vulnerabilities."
    if s2.button("📐 UI UX"): p_cmd = "Suggest 3 ways to make this app look even more professional."
    if s3.button("🧠 Sync Memory"): p_cmd = "Read memory_general.json and summarize our progress."

    query = st.chat_input("Command the Nexus...") or p_cmd

if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with chat_box.chat_message("user"): st.markdown(query)
    
    with chat_box.chat_message("assistant"):
        with st.spinner("Generating..."):
            try:
                comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": query}])
                ans = comp.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()
            except Exception as e: st.error(e)
