import streamlit as st
from google import genai
from tavily import TavilyClient
import json
import datetime
from github import Github

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="NEXUS COMMAND", layout="wide")

st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: #ffffff; }
    .stButton>button { background: #3a7bd5; color: white; border-radius: 12px; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: #0b0e14; border-right: 1px solid #3a7bd5; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo_name = st.secrets["GH_REPO"]
except Exception as e:
    st.error("📡 AUTH ERROR: Please check your Streamlit Secrets.")
    st.stop()

# --- 3. CORE FUNCTIONS ---
def update_file(path, content, msg):
    repo = g.get_repo(repo_name)
    try:
        sha = repo.get_contents(path).sha
        repo.update_file(path, msg, content, sha)
    except:
        repo.create_file(path, msg, content)

# --- 4. UI ---
# Load User Name from local memory or GitHub
if 'user_name' not in st.session_state:
    try:
        repo = g.get_repo(repo_name)
        mem = json.loads(repo.get_contents("memory.json").decoded_content.decode())
        st.session_state.user_name = mem.get("user_name", "Commander")
    except:
        st.session_state.user_name = "Adil"

with st.sidebar:
    st.title("🧬 NEXUS CORE")
    st.success("BRAIN: ONLINE")
    st.write(f"USER: **{st.session_state.user_name}**")
    
    with st.expander("👤 IDENTITY"):
        new_name = st.text_input("Name", value=st.session_state.user_name)
        if st.button("SYNC"):
            update_file("memory.json", json.dumps({"user_name": new_name}), "Update Identity")
            st.session_state.user_name = new_name
            st.rerun()

st.title(f"Greetings, {st.session_state.user_name}")

# COMMAND AREA
task = st.text_area("Next Phase Command:", placeholder="e.g. Add a system status light...")

if st.button("🚀 INITIATE EVOLUTION"):
    try:
        with st.status("🧬 Thinking...", expanded=True):
            res = tavily.search(query=f"Streamlit code for {task}", search_depth="basic")
            prompt = f"Rewrite app.py. Keep all existing GitHub/Memory logic. Add {task}. Use {res}. RAW CODE ONLY."
            # We use gemini-1.5-flash here for maximum stability during tests
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            st.session_state.draft = response.text
            st.rerun()
    except Exception as e:
        st.error(f"Brain Glitch: {e}. Please try a simpler command.")

if "draft" in st.session_state:
    st.subheader("🧬 Proposed DNA")
    st.code(st.session_state.draft, language="python")
    if st.button("✅ PERMIT"):
        update_file("app.py", st.session_state.draft, "🧬 EVOLUTION")
        st.balloons()
