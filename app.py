import streamlit as st
from google import genai
from tavily import TavilyClient
import json
from github import Github

st.set_page_config(page_title="NEXUS COMMAND", layout="wide")

# Corrected Styling
st.markdown("""
    <style>
    .main { background: #0f0c29; color: white; }
    .stButton>button { background: #3a7bd5; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# Auth
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo_name = st.secrets["GH_REPO"]
except:
    st.error("📡 AUTH ERROR: Check Secrets names (GH_TOKEN, GH_REPO, etc.)")
    st.stop()

# Memory Sync
if 'user_name' not in st.session_state:
    try:
        repo = g.get_repo(repo_name)
        mem = json.loads(repo.get_contents("memory.json").decoded_content.decode())
        st.session_state.user_name = mem.get("user_name", "Commander")
    except:
        st.session_state.user_name = "Adil"

with st.sidebar:
    st.title("🧬 NEXUS CORE")
# New Status Light Feature
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="width: 12px; height: 12px; background-color: #00ff00; border-radius: 50%; box-shadow: 0 0 10px #00ff00;"></div>
            <span style="color: #00ff00; font-weight: bold; font-family: monospace;">Neural Link: Active</span>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"USER: **{st.session_state.user_name}**")
    new_name = st.text_input("Edit Name", value=st.session_state.user_name)
    if st.button("SYNC"):
        repo = g.get_repo(repo_name)
        content = json.dumps({"user_name": new_name})
        try:
            f = repo.get_contents("memory.json")
            repo.update_file(f.path, "Update Identity", content, f.sha)
        except:
            repo.create_file("memory.json", "Create Identity", content)
        st.session_state.user_name = new_name
        st.rerun()

st.title(f"Greetings, {st.session_state.user_name}")
task = st.text_area("Evolution Command:", placeholder="e.g. Add a system status light...")

if st.button("🚀 INITIATE"):
    try:
        with st.status("🧬 Thinking...", expanded=True):
            search = tavily.search(query=f"Streamlit code {task}", search_depth="basic")
            # FIXED MODEL STRING BELOW
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=f"Rewrite app.py to add {task} using {search}. Keep GitHub/Memory logic. RAW CODE ONLY."
            )
            st.session_state.draft = response.text
            st.rerun()
    except Exception as e:
        st.error(f"Brain Glitch: {e}")

if "draft" in st.session_state:
    st.code(st.session_state.draft, language="python")
    if st.button("✅ PERMIT"):
        repo = g.get_repo(repo_name)
        f = repo.get_contents("app.py")
        repo.update_file(f.path, "🧬 EVOLUTION", st.session_state.draft, f.sha)
        st.success("DNA Updated. Rebooting...")
